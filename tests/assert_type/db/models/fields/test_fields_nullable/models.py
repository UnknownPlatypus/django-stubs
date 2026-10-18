from __future__ import annotations

import datetime
import decimal
from typing import assert_type

from django.db import models
from django.db.models import IntegerField, OuterRef, Subquery
from typing_extensions import TypeVar

# Generic subclasses default their type vars like the parent field, so bare calls resolve without the plugin
_ST_Text = TypeVar("_ST_Text", contravariant=True, default=str)
_GT_Text = TypeVar("_GT_Text", covariant=True, default=str)
_ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
_GT_Int = TypeVar("_GT_Int", covariant=True, default=int)


class MyModel(models.Model):
    text_nullable = models.CharField(max_length=100, null=True)
    text = models.CharField(max_length=100)


def nullable_field_with_strict_optional_true() -> None:
    assert_type(MyModel().text, str)
    assert_type(MyModel().text_nullable, str | None)
    MyModel().text = None  # type: ignore[assignment]  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-assignment]
    MyModel().text_nullable = None


class BlankNotNull(models.Model):
    notnulltext = models.CharField(max_length=1, blank=True, null=False)


def blank_and_not_null_charfield_does_not_allow_none() -> None:
    BlankNotNull(notnulltext=None)  # type: ignore[misc]


class HtmlField(models.TextField[_ST_Text, _GT_Text]): ...


class IntWrap(models.IntegerField[_ST_Int, _GT_Int]): ...


class Article(models.Model):
    body = HtmlField()
    body_nullable = HtmlField(null=True)
    count = IntWrap()
    count_nullable = IntWrap(null=True)


def nullable_subclass_inherits_null_overload() -> None:
    assert_type(Article().body, str)
    assert_type(Article().body_nullable, str | None)  # pyright: ignore[reportAssertTypeFailure]
    assert_type(Article().count, int)
    assert_type(Article().count_nullable, int | None)  # pyright: ignore[reportAssertTypeFailure]


class SubqueryArticle(models.Model):
    pass


def direct_field_null_true_does_not_trigger_nullability_check() -> None:
    field = models.IntegerField(null=True)
    assert_type(field, IntegerField[float | int | str | None, int | None])
    not_null_field = models.IntegerField(null=False)
    assert_type(not_null_field, IntegerField[float | int | str, int])
    SubqueryArticle.objects.annotate(
        other_id=Subquery(
            SubqueryArticle.objects.filter(id=OuterRef("id")).values_list("id", flat=True)[:1],
            output_field=models.IntegerField(null=True),
        )
    )


def field_null_true_expression_does_not_trigger_nullability_check() -> None:
    def take_field(f: models.Field) -> None:
        return None

    take_field(models.IntegerField(null=True))
    take_field(models.IntegerField(null=False))


class HTMLField(models.TextField): ...


class BareIntWrap(models.IntegerField): ...


class FieldMixin: ...


class MySlugField(models.SlugField, FieldMixin): ...


class BareArticle(models.Model):
    body = HTMLField()
    body_nullable = HTMLField(null=True)
    count_nullable = BareIntWrap(null=True)
    slug_nullable = MySlugField(null=True)


def nullable_field_subclass_without_explicit_type_vars() -> None:
    assert_type(BareArticle().body, str)
    assert_type(BareArticle().body_nullable, str | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(BareArticle().count_nullable, int | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(BareArticle().slug_nullable, str | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]


class PositionalArgs(models.Model):
    amount = models.DecimalField(None, None, 10, 2, null=True)  # max_digits/decimal_places positional
    day = models.DateField(None, None, False, False, null=True)  # auto_now/auto_now_add positional
    moment = models.TimeField(None, None, False, False, null=True)
    stamp = models.DateTimeField(None, None, False, False, null=True)
    addr = models.GenericIPAddressField(None, None, "both", False, null=True)  # protocol/unpack_ipv4


def positional_overload_args_with_null_true_select_nullable_overload() -> None:
    """Fields whose nullable overload has extra args must accept them positionally with `null=True`."""
    instance = PositionalArgs()
    assert_type(instance.amount, decimal.Decimal | None)
    assert_type(instance.day, datetime.date | None)
    assert_type(instance.moment, datetime.time | None)
    assert_type(instance.stamp, datetime.datetime | None)
    assert_type(instance.addr, str | None)


class MyPk(models.IntegerField[int, int]): ...


class Target(models.Model):
    code = MyPk(primary_key=True)


class Book(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=True)


def nullable_fk_to_custom_pk_without_type_params_does_not_crash() -> None:
    # A pinned custom PK has no type params, so `target_id` can't carry the column's `| None` yet,
    # but it must not crash the plugin.
    assert_type(Book().target_id, int | None)  # type: ignore[assert-type]  # pyright: ignore[reportAssertTypeFailure, reportAttributeAccessIssue, reportUnknownMemberType]  # ty: ignore[type-assertion-failure, unresolved-attribute]
