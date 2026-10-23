from __future__ import annotations

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Kind(models.TextChoices):
    A = "a"


def kind_choices() -> dict[str, str]:
    return {"a": "A"}


# Every field accepts what `Field.choices` accepts: a `Choices` class, a mapping or a callable.
# ty drops `type[Choices]` from the union: https://github.com/astral-sh/ty/issues/4551
def field_choices_input() -> None:
    models.FileField(choices=Kind)  # ty: ignore[invalid-argument-type]
    models.ForeignKey("auth.User", models.CASCADE, choices={"a": "A"})
    models.OneToOneField("auth.User", models.CASCADE, choices=kind_choices)
    models.ManyToManyField("auth.User", choices=Kind)  # ty: ignore[invalid-argument-type]
    ArrayField(models.CharField(), choices=Kind)  # ty: ignore[invalid-argument-type]
    PointField(choices=kind_choices)
