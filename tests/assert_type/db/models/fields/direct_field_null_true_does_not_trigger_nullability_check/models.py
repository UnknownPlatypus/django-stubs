from __future__ import annotations

from typing import assert_type

from django.db import models
from django.db.models import IntegerField
from django.db.models.expressions import OuterRef, Subquery


class Article(models.Model):
    pass


def direct_field_null_true_does_not_trigger_nullability_check() -> None:
    null_field = models.IntegerField(null=True)
    assert_type(null_field, IntegerField[float | int | str | None, int | None])  # ty: ignore[type-assertion-failure] # regressed in ty >=0.0.40

    not_null_field = models.IntegerField(null=False)
    assert_type(not_null_field, IntegerField[float | int | str, int])

    Article.objects.annotate(
        other_id=Subquery(
            Article.objects.filter(id=OuterRef("id")).values_list("id", flat=True)[:1],
            output_field=models.IntegerField(null=False),
        )
    )
