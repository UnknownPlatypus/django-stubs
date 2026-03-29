from mypy.nodes import Expression, StrExpr
from mypy.plugin import MethodContext
from mypy.types import Instance, TypeType
from mypy.types import Type as MypyType

from mypy_django_plugin.django.context import DjangoContext
from mypy_django_plugin.lib import helpers


def _get_model_reference(ctx: MethodContext) -> tuple[str, Expression] | None:
    app_label = helpers.get_call_argument_by_name(ctx, "app_label")
    model_name = helpers.get_call_argument_by_name(ctx, "model_name")

    if isinstance(app_label, StrExpr):
        if model_name is None:
            return app_label.value, app_label
        if isinstance(model_name, StrExpr):
            return f"{app_label.value}.{model_name.value}", model_name

    return None


def resolve_model_for_get_model(ctx: MethodContext, django_context: DjangoContext) -> MypyType:
    model_reference = _get_model_reference(ctx)
    if model_reference is None:
        return ctx.default_return_type

    lazy_reference, error_context = model_reference
    typechecker_api = helpers.get_typechecker_api(ctx)
    fullname = django_context.model_class_fullnames_by_label_lower.get(lazy_reference.lower())
    if fullname is None:
        typechecker_api.fail("Could not match lazy reference with any model", error_context)
        return ctx.default_return_type

    model_info = helpers.lookup_fully_qualified_typeinfo(typechecker_api, fullname)
    if model_info is None:
        return ctx.default_return_type
    return TypeType(Instance(model_info, []))
