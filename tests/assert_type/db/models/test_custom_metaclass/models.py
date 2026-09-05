"""Models built by a `ModelBase` subclass."""

from __future__ import annotations

from typing import Any, assert_type

from django.db import models
from django.db.models.base import ModelBase
from typing_extensions import override


class MyBase(ModelBase):
    pass


class MyModel(models.Model, metaclass=MyBase):
    pass


class Other(MyModel):
    pass


class This(MyModel):
    field = models.ForeignKey(Other, on_delete=models.CASCADE)  # pyright: ignore[reportUnknownVariableType]


class LoudBase(ModelBase):
    @override
    def __getattr__(cls, name: str) -> Any:
        if name.startswith("loud_"):
            return 42
        raise AttributeError(name)


class Loud(models.Model, metaclass=LoudBase):
    pass


def custom_metaclass_keeps_field_resolution() -> None:
    # pyright and ty don't resolve the untyped `ForeignKey` the way the mypy plugin and pyrefly do
    assert_type(This(field=Other()).field, Other)  # pyright: ignore[reportUnknownMemberType, reportAssertTypeFailure]  # ty: ignore[type-assertion-failure]


def custom_metaclass_keeps_the_objects_fallback() -> None:
    assert_type(Other.objects, models.Manager[Other])
    Other.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]


def custom_getattr_answers_for_itself() -> None:
    assert_type(Loud.loud_thing, Any)
