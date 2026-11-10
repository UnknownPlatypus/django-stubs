from __future__ import annotations

from typing import Any, assert_type

from django.db import models


class Tag(models.Model):
    pass


class Article(models.Model):
    tags = models.ManyToManyField(Tag)


def test_direct_assignment_is_rejected() -> None:
    # Django raises `TypeError`, the related set is changed through `tags.set()`.
    Article().tags = [Tag()]  # type: ignore[assignment]  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[bad-assignment]  # ty: ignore[invalid-assignment]
    # only the mypy plugin checks model init kwargs
    Article(tags=[Tag()])  # type: ignore[misc]


def test_value_from_object(field: models.ManyToManyField[Tag, Any]) -> None:
    assert_type(field.value_from_object(Article()), list[Tag])
