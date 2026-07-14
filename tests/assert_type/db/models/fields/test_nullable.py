from __future__ import annotations

import datetime
import decimal
from typing import Any

from django.db import models
from typing_extensions import assert_type


def positional_overload_args_with_null_true_select_nullable_overload() -> None:
    """Fields whose nullable overload has extra args must accept them positionally with `null=True`.

    If the nullable overload marks these args keyword-only while the fallback keeps them positional,
    a positional call silently binds the non-nullable fallback and drops the `| None` read type.
    """

    class MyModel(models.Model):
        amount = models.DecimalField(None, None, 10, 2, null=True)  # max_digits/decimal_places positional
        day = models.DateField(None, None, False, False, null=True)  # auto_now/auto_now_add positional
        moment = models.TimeField(None, None, False, False, null=True)
        stamp = models.DateTimeField(None, None, False, False, null=True)
        addr = models.GenericIPAddressField(None, None, "both", False, null=True)  # protocol/unpack_ipv4

    # ty infers the non-nullable read type here (it doesn't reflect nullable-overload reads --
    # regressed in ty >=0.0.40, same as the custom-field cases); mypy/pyright/pyrefly are correct.
    instance = MyModel()
    assert_type(instance.amount, decimal.Decimal | None)  # ty: ignore[type-assertion-failure]
    assert_type(instance.day, datetime.date | None)  # ty: ignore[type-assertion-failure]
    assert_type(instance.moment, datetime.time | None)  # ty: ignore[type-assertion-failure]
    assert_type(instance.stamp, datetime.datetime | None)  # ty: ignore[type-assertion-failure]
    assert_type(instance.addr, str | None)  # ty: ignore[type-assertion-failure]


def field_null_true_expression_does_not_trigger_nullability_check() -> None:
    """
    Field[Any, Any] as function type arg should accept both nullable and non-nullable fields
    """

    def take_field(f: models.Field[Any, Any]) -> None:
        return None

    take_field(models.IntegerField(null=True))
    take_field(models.IntegerField(null=False))
