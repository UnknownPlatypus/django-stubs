from __future__ import annotations

from typing import Any, ClassVar

from django.db import models
from django.db.models.fields.related_descriptors import (
    RelatedManager,
    ReverseManyToOneDescriptor,
    create_reverse_many_to_one_manager,
)
from typing_extensions import TypeVar, assert_type

_To = TypeVar("_To", bound=models.Model)
_To_QS = TypeVar("_To_QS", bound=models.QuerySet[Any])


class Other(models.Model):
    explicit_descriptor: ClassVar[ReverseManyToOneDescriptor[MyModel]]


class MyModel(models.Model):
    rel = models.ForeignKey[Other, Other](Other, on_delete=models.CASCADE, related_name="explicit_descriptor")


assert_type(Other().explicit_descriptor, RelatedManager[MyModel, models.QuerySet[MyModel, MyModel]])  # ty: ignore[type-assertion-failure]


class CustomDescriptor(ReverseManyToOneDescriptor[MyModel, models.QuerySet[MyModel, MyModel]]):
    def custom_method(self) -> int:
        raise NotImplementedError


class WithCustomDescriptor(models.Model):
    custom_descriptor: ClassVar[CustomDescriptor]


# Class-level access returns `Self`, preserving descriptor subclasses and their members
assert_type(WithCustomDescriptor.custom_descriptor, CustomDescriptor)
assert_type(WithCustomDescriptor.custom_descriptor.custom_method(), int)


class PassThroughDescriptor(ReverseManyToOneDescriptor[_To, _To_QS]): ...


class WithPassThroughDescriptor(models.Model):
    passthrough_descriptor: ClassVar[PassThroughDescriptor[MyModel, models.QuerySet[MyModel, MyModel]]]


# Class-level access returns `Self`, preserving a generic subclass and its parameterization
assert_type(
    WithPassThroughDescriptor.passthrough_descriptor, PassThroughDescriptor[MyModel, models.QuerySet[MyModel, MyModel]]
)

# Ensure `create_reverse_many_to_one_manager` pass generic params correctly
reverse_many_to_one_manager = create_reverse_many_to_one_manager(
    superclass=MyModel._default_manager.__class__,
    rel=MyModel.rel.field.remote_field,  # pyrefly: ignore[missing-attribute]
)
assert_type(MyModel._default_manager.__class__, type[models.Manager[MyModel, models.QuerySet[MyModel, MyModel]]])
assert_type(reverse_many_to_one_manager, type[RelatedManager[MyModel, models.QuerySet[MyModel, MyModel]]])  # ty: ignore[type-assertion-failure]
