from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import AutoField
from django.db.models.fields.related import RelatedField
from mypy.nodes import AssignmentStmt, NameExpr, TypeInfo
from mypy.typeanal import make_optional_type
from mypy.types import AnyType, Instance, ProperType, TypeOfAny, get_proper_type
from mypy.types import Type as MypyType

from mypy_django_plugin.exceptions import UnregisteredModelError
from mypy_django_plugin.lib import fullnames, helpers
from mypy_django_plugin.transformers import manytomany

if TYPE_CHECKING:
    from django.db.models.options import _AnyField
    from mypy.plugin import FunctionContext

    from mypy_django_plugin.django.context import DjangoContext


def _get_current_field_from_assignment(ctx: FunctionContext, django_context: DjangoContext) -> _AnyField | None:
    outer_model_info = helpers.get_typechecker_api(ctx).scope.active_class()
    if outer_model_info is None or not helpers.is_model_type(outer_model_info):
        return None

    field_name = None
    for stmt in outer_model_info.defn.defs.body:
        if isinstance(stmt, AssignmentStmt):
            if stmt.rvalue == ctx.context:
                if not isinstance(stmt.lvalues[0], NameExpr):
                    return None
                field_name = stmt.lvalues[0].name
                break
    if field_name is None:
        return None

    model_cls = django_context.get_model_class_by_fullname(outer_model_info.fullname)
    if model_cls is None:
        return None

    try:
        return model_cls._meta.get_field(field_name)
    except FieldDoesNotExist:
        return None


def fill_descriptor_types_for_related_field(ctx: FunctionContext, django_context: DjangoContext) -> MypyType:
    current_field = _get_current_field_from_assignment(ctx, django_context)
    if current_field is None:
        return AnyType(TypeOfAny.from_error)

    assert isinstance(current_field, RelatedField)

    try:
        related_model_cls = django_context.get_field_related_model_cls(current_field)
    except UnregisteredModelError:
        return AnyType(TypeOfAny.from_error)

    default_related_field_type = set_descriptor_types_for_field(ctx)
    if len(default_related_field_type.args) != 2:
        return default_related_field_type

    # self reference with abstract=True on the model where ForeignKey is defined
    current_model_cls = current_field.model
    if current_model_cls._meta.abstract and current_model_cls == related_model_cls:
        # for all derived non-abstract classes, set variable with this name to
        # __get__/__set__ of ForeignKey of derived model
        for model_cls in django_context.all_registered_model_classes:
            if issubclass(model_cls, current_model_cls) and not model_cls._meta.abstract:
                derived_model_info = helpers.lookup_class_typeinfo(helpers.get_typechecker_api(ctx), model_cls)
                if derived_model_info is not None:
                    fk_ref_type = Instance(derived_model_info, [])
                    derived_fk_type = helpers.reparametrize_field_type(
                        default_related_field_type, set_type=fk_ref_type, get_type=fk_ref_type
                    )
                    helpers.add_new_sym_for_info(derived_model_info, name=current_field.name, sym_type=derived_fk_type)

    related_model = related_model_cls
    related_model_to_set = related_model_cls
    if related_model_to_set._meta.proxy_for_model is not None:
        related_model_to_set = related_model_to_set._meta.proxy_for_model

    typechecker_api = helpers.get_typechecker_api(ctx)

    related_model_info = helpers.lookup_class_typeinfo(typechecker_api, related_model)
    related_model_type: ProperType
    if related_model_info is None:
        # maybe no type stub
        related_model_type = AnyType(TypeOfAny.unannotated)
    else:
        related_model_type = Instance(related_model_info, [])

    related_model_to_set_info = helpers.lookup_class_typeinfo(typechecker_api, related_model_to_set)
    related_model_to_set_type: ProperType
    if related_model_to_set_info is None:
        # maybe no type stub
        related_model_to_set_type = AnyType(TypeOfAny.unannotated)
    else:
        related_model_to_set_type = Instance(related_model_to_set_info, [])

    is_nullable = helpers.get_bool_call_argument_by_name(ctx, "null", default=False)

    set_type: MypyType = related_model_to_set_type
    get_type: MypyType = related_model_type
    if is_nullable:
        set_type = make_optional_type(set_type)
        get_type = make_optional_type(get_type)

    # replace Any with referred_to_type
    return helpers.reparametrize_field_type(
        default_related_field_type, set_type=set_type, get_type=get_type, is_nullable=is_nullable
    )


def set_descriptor_types_for_field_callback(ctx: FunctionContext, django_context: DjangoContext) -> MypyType:
    current_field = _get_current_field_from_assignment(ctx, django_context)
    if current_field is not None:
        if isinstance(current_field, AutoField):
            return set_descriptor_types_for_field(ctx, is_set_nullable=True)

    return set_descriptor_types_for_field(ctx)


def set_descriptor_types_for_field(ctx: FunctionContext, *, is_set_nullable: bool = False) -> Instance:
    default_return_type = cast("Instance", ctx.default_return_type)
    if len(default_return_type.args) != 2:
        # Explicitly bound fields. For ex:
        # `class CustomValueField(fields.Field[CustomFieldValue | int, CustomFieldValue])`
        return default_return_type

    is_nullable = helpers.get_bool_call_argument_by_name(ctx, "null", default=False)

    is_primary_key = helpers.get_bool_call_argument_by_name(ctx, "primary_key", default=False)
    default_expr = helpers.get_call_argument_by_name(ctx, "default")
    if default_expr is not None:
        is_set_nullable = is_primary_key

    set_type = default_return_type.args[0]
    get_type = default_return_type.args[1]
    # `null=True` makes both directions optional; `primary_key` + `default` only relaxes writes.
    # The stub `__init__` overloads already encode this for direct concrete-field calls; this
    # hook re-derives it for the cases overloads cannot see (auto-reparametrized custom field
    # subclasses, fallback-overload resolutions).
    # FileField is excluded: FileDescriptor.__get__ always returns a FieldFile (wrapping None)
    # and its __set__ already accepts None, so its stub overrides are authoritative.
    if default_return_type.type.has_base(fullnames.FILE_FIELD_FULLNAME):
        return default_return_type
    # Only fold `None` when the field's own type parameters *are* its set/get types (the direct
    # case: CharField, IntegerField, ForeignKey, ...). "Wrapper" fields such as ArrayField
    # parametrize themselves on element types (`ArrayField[_ST_Array, _GT_Array]` extending
    # `Field[Sequence[_ST_Array] | Combinable, list[_GT_Array]]`); folding `None` into their args
    # would wrongly make the *element* optional (`list[int | None]`) instead of the column
    # (`list[int] | None`). Such fields cannot encode column nullability through their own
    # parameters, so — like every checker without the plugin — we leave them unchanged.
    field_args = helpers.get_field_type_args(default_return_type)
    is_direct = field_args is not None and field_args.set == set_type and field_args.get == get_type
    if is_direct:
        if is_set_nullable or is_nullable:
            set_type = make_optional_type(set_type)
        if is_nullable:
            get_type = make_optional_type(get_type)
    return default_return_type.copy_modified(args=[set_type, get_type])


def transform_into_proper_return_type(ctx: FunctionContext, django_context: DjangoContext) -> MypyType:
    default_return_type = get_proper_type(ctx.default_return_type)
    assert isinstance(default_return_type, Instance)

    outer_model_info = helpers.get_typechecker_api(ctx).scope.active_class()
    if outer_model_info is None or not helpers.is_model_type(outer_model_info):
        return default_return_type

    assert isinstance(outer_model_info, TypeInfo)

    if default_return_type.type.has_base(fullnames.MANYTOMANY_FIELD_FULLNAME):
        return manytomany.fill_model_args_for_many_to_many_field(
            ctx=ctx, model_info=outer_model_info, django_context=django_context
        )
    if helpers.has_any_of_bases(default_return_type.type, fullnames.RELATED_FIELDS_CLASSES):
        return fill_descriptor_types_for_related_field(ctx, django_context)

    return set_descriptor_types_for_field_callback(ctx, django_context)
