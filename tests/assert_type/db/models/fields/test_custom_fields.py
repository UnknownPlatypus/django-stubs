from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, overload

from django.db import models
from django.db.models.expressions import Combinable, F
from django.db.models.fields import _GT, _ST
from typing_extensions import TypeVar, Unpack, assert_type

if TYPE_CHECKING:
    from django_stubs_ext import FieldInitKwargs

T = TypeVar("T")


class CustomFieldValue: ...


def custom_generic_field_override_typevar_defaults() -> None:
    class GenericField(models.Field[_ST, _GT]): ...

    class MyModel(models.Model):
        field = GenericField[CustomFieldValue | int, CustomFieldValue]()
        # A nullable custom field is expressed by widening the explicit get/set parameters;
        # this resolves identically on every type checker (no plugin needed).
        null_field = GenericField[CustomFieldValue | int | None, CustomFieldValue | None]()

    instance = MyModel()
    assert_type(instance.field, CustomFieldValue)
    assert_type(instance.null_field, CustomFieldValue | None)


def single_type_field() -> None:
    class SingleTypeField(models.Field[T, T]): ...

    class MyModel(models.Model):
        field = SingleTypeField[bool]()
        explicit_null_field = SingleTypeField[bool | None]()

    instance = MyModel()
    assert_type(instance.field, bool)
    assert_type(instance.explicit_null_field, bool | None)


def custom_explicit_get_set_field() -> None:
    # A field bound to concrete (non-TypeVar) get/set types is itself non-generic, so neither
    # the stubs nor the plugin can track `null=` on it — reparametrize with `| None` for nullable.
    class CustomValueField(models.Field[CustomFieldValue | int, CustomFieldValue]): ...

    class MyModel(models.Model):
        field = CustomValueField()
        null_field = CustomValueField(null=True)

    instance = MyModel()
    assert_type(instance.field, CustomFieldValue)
    assert_type(instance.null_field, CustomFieldValue)  # `null=True` is not reflected (see note above)
    instance.field = CustomFieldValue()
    instance.field = 12
    instance.field = "NoNo"  # type: ignore[assignment] # pyrefly:ignore[bad-argument-type] # ty:ignore[invalid-assignment] # pyright:ignore[reportAttributeAccessIssue]


def custom_generic_field() -> None:
    _ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str | Combinable)
    _GT_Int = TypeVar("_GT_Int", covariant=True, default=int)

    class CustomSmallIntegerField(models.SmallIntegerField[_ST_Int, _GT_Int]): ...

    class MyModel(models.Model):
        field = CustomSmallIntegerField()
        null_field = CustomSmallIntegerField(null=True)

    instance = MyModel()
    assert_type(instance.field, int)
    assert_type(instance.null_field, int | None)  # pyright: ignore[reportAssertTypeFailure] # ty: ignore[type-assertion-failure] # regressed in ty >=0.0.40
    instance.field = 1.2
    instance.field = 12
    instance.field = "12"
    instance.field = F("id")
    instance.field = CustomFieldValue()  # type: ignore[assignment] # pyrefly:ignore[bad-argument-type] # ty:ignore[invalid-assignment] # pyright:ignore[reportAttributeAccessIssue]


def additional_typevar_field() -> None:
    _ST_Custom = TypeVar("_ST_Custom", contravariant=True, default=CustomFieldValue | int)
    _GT_Custom = TypeVar("_GT_Custom", covariant=True, default=CustomFieldValue)

    class AdditionalTypeVarField(models.Field[_ST_Custom, _GT_Custom], Generic[T, _ST_Custom, _GT_Custom]): ...

    class MyModel(models.Model):
        field = AdditionalTypeVarField[bool]()
        null_field = AdditionalTypeVarField[bool, CustomFieldValue | int | None, CustomFieldValue | None]()

    instance = MyModel()
    assert_type(instance.field, CustomFieldValue)
    assert_type(instance.null_field, CustomFieldValue | None)


def field_implicit_any() -> None:
    # This is inferred as models.Field[Any, Any]
    class FieldImplicitAny(models.Field): ...

    class MyModel(models.Model):
        field = FieldImplicitAny()
        null_field = FieldImplicitAny(null=True)

    instance = MyModel()
    assert_type(instance.field, Any)
    assert_type(instance.null_field, Any)  # type:ignore[assert-type] # Mypy says `Any | None` which is a bit odd


def field_explicit_any() -> None:
    class FieldExplicitAny(models.Field[Any, Any]): ...

    class MyModel(models.Model):
        field = FieldExplicitAny()
        null_field = FieldExplicitAny(null=True)

    instance = MyModel()
    assert_type(instance.field, Any)
    assert_type(instance.null_field, Any)


def field_two_typevar_form_is_still_accepted() -> None:
    class LegacyField(models.Field[CustomFieldValue | int, CustomFieldValue]): ...

    class MyModel(models.Model):
        field = LegacyField()
        null_field = LegacyField(null=True)

    instance = MyModel()
    assert_type(instance.field, CustomFieldValue)
    # Concrete 2-typevar form is non-generic, so `null=True` is not reflected on any checker.
    assert_type(instance.null_field, CustomFieldValue)
    instance.field = CustomFieldValue()
    instance.field = 12


def field_two_typevar_form_in_user_annotation() -> None:
    # Legacy `field: Field[A, B] = CustomField()` annotations with a 2-typevar `CustomField`
    class CustomField(models.Field[CustomFieldValue | int, CustomFieldValue]): ...

    class MyModel(models.Model):
        field: models.Field[CustomFieldValue | int, CustomFieldValue] = CustomField()

    instance = MyModel()
    assert_type(instance.field, CustomFieldValue)
    instance.field = CustomFieldValue()
    instance.field = 12
    instance.field = "no"  # type: ignore[assignment]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-assignment]  # pyright: ignore[reportAttributeAccessIssue]


def nullable_subclass_via_explicit_params() -> None:
    # The cross-checker recipe for a nullable custom field: redeclare the generic parameters
    # with `| None`. No plugin required.
    _ST_Text = TypeVar("_ST_Text", contravariant=True, default=str | int | Combinable)
    _GT_Text = TypeVar("_GT_Text", covariant=True, default=str)

    class HtmlField(models.TextField[_ST_Text, _GT_Text]): ...

    class Article(models.Model):
        body = HtmlField()
        body_nullable = HtmlField[str | int | Combinable | None, str | None]()

    assert_type(Article().body, str)
    assert_type(Article().body_nullable, str | None)


def nullable_field_subclass_without_explicit_type_vars() -> None:
    """
    The mypy plugin reparametrizes bare subclasses so `null=True` works without extra typevars.

    Other checkers cannot, so the nullable reads keep the non-null get-type there.
    """

    class HTMLField(models.TextField): ...

    class IntWrap(models.IntegerField): ...

    class FieldMixin: ...

    class MySlugField(models.SlugField, FieldMixin): ...

    class Article(models.Model):
        body = HTMLField()
        body_nullable = HTMLField(null=True)
        count_nullable = IntWrap(null=True)
        slug_nullable = MySlugField(null=True)

    assert_type(Article().body, str)
    assert_type(Article().body_nullable, str | None)  # pyrefly: ignore[assert-type] # ty: ignore[type-assertion-failure] # pyright: ignore[reportAssertTypeFailure]
    assert_type(Article().count_nullable, int | None)  # pyrefly: ignore[assert-type] # ty: ignore[type-assertion-failure] # pyright: ignore[reportAssertTypeFailure]
    assert_type(Article().slug_nullable, str | None)  # pyrefly: ignore[assert-type] # ty: ignore[type-assertion-failure] # pyright: ignore[reportAssertTypeFailure]


def custom_model_field_override_init_via_overloads() -> None:
    """The documented recipe: redeclare `__init__` overloads to bind nullability per checker."""
    _ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
    _GT_Int = TypeVar("_GT_Int", covariant=True, default=int)

    class MyIntegerField(models.IntegerField[_ST_Int, _GT_Int]):
        @overload
        def __init__(  # nullable: read and write accept None
            self: MyIntegerField[float | int | str | None, int | None],
            verbose_name: str | None = None,
            name: str | None = None,
            *,
            null: Literal[True],
            **kwargs: Unpack[FieldInitKwargs[float | int | str | None]],
        ) -> None: ...
        @overload
        def __init__(  # fallback: dynamic flags keep the class defaults
            self,
            verbose_name: str | None = None,
            name: str | None = None,
            *,
            null: bool = False,
            **kwargs: Unpack[FieldInitKwargs[float | int | str]],
        ) -> None: ...
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

    class User(models.Model):
        custom_int = MyIntegerField(null=False)
        custom_int_nullable = MyIntegerField(null=True)

    # a bad kwarg is rejected through the Unpack'd TypedDict, on every checker
    MyIntegerField(nul=True)  # type: ignore[call-overload] # pyrefly: ignore[no-matching-overload] # ty: ignore[no-matching-overload] # pyright: ignore[reportCallIssue] # fmt: skip

    assert_type(User().custom_int, int)
    assert_type(User().custom_int_nullable, int | None)  # ty: ignore[type-assertion-failure] # regressed in ty >=0.0.40
