"""`objects` resolves through `ModelBase.__getattr__` unless the model declares its own manager."""

from __future__ import annotations

from typing import assert_type

from django.db import models


class CategoryManager(models.Manager["Category"]):
    pass


class Category(models.Model):
    objects = CategoryManager()
    secondary = CategoryManager()


class Post(models.Model):
    """No declared manager, `objects` only resolves through `ModelBase.__getattr__`."""


def manager_access_on_class_is_allowed() -> None:
    # A declared manager keeps its own type, exactly like any other class attribute
    assert_type(Category.objects, CategoryManager)
    assert_type(Category.secondary, CategoryManager)
    assert_type(Post.objects, models.Manager[Post])


def unknown_attribute_is_still_an_error() -> None:
    # `Literal["objects"]` must not turn `__getattr__` into a catch-all
    Category.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]
    Category().not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # pyrefly: ignore[missing-attribute]  # ty: ignore[unresolved-attribute]
