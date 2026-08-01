"""Regression test for https://github.com/typeddjango/django-stubs/issues/2911.

A TypeVar with a forward-referenced bound used in a QuerySet subclass
caused 'Must not defer during final iteration' crash in mypy.
"""

from __future__ import annotations

from typing import Any, assert_type

from django.db import models
from django.db.models.query import QuerySet
from typing_extensions import TypeVar, override

T = TypeVar("T", bound="MyModel")


class MyModelQuerySet(QuerySet[T]):
    pass


class MyModel(models.Model):
    class Meta:
        app_label = "myapp"


class CustomManager(models.Manager["OtherModel"]):
    def manager_method(self) -> str:
        return ""


class OtherQuerySet(models.QuerySet["OtherModel"]):
    def queryset_method(self) -> int:
        return 0

    @classmethod
    @override
    def as_manager(cls) -> CustomManager:  # type: ignore[override]  # pyrefly: ignore[bad-override]
        return CustomManager.from_queryset(cls)()


class OtherModel(models.Model):
    class Meta:
        app_label = "myapp"


# `from_queryset` returns `type[Self]`, preserving manager subclasses and their members
assert_type(CustomManager.from_queryset(OtherQuerySet), type[CustomManager])
assert_type(CustomManager.from_queryset(OtherQuerySet)().manager_method(), str)


class TypedManager(models.Manager["OtherModel", OtherQuerySet]):
    pass


def check_declared_queryset_param(typed_manager: TypedManager) -> None:
    """The declared queryset param flows through every chainable method, no plugin involved."""
    assert_type(typed_manager.get_queryset(), OtherQuerySet)
    assert_type(typed_manager.all(), OtherQuerySet)
    assert_type(typed_manager.filter(), OtherQuerySet)
    assert_type(typed_manager.only("id"), OtherQuerySet)
    assert_type(typed_manager.union(typed_manager.all()), OtherQuerySet)
    assert_type(typed_manager.all().queryset_method(), int)
    # Methods building a differently-typed queryset stay plain `QuerySet`
    assert_type(typed_manager.values("id"), QuerySet[OtherModel, dict[str, Any]])
