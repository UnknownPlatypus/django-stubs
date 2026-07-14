from __future__ import annotations

import uuid
from typing import Any, assert_type

from django.contrib.postgres.fields import ArrayField
from django.db import models


def nullable_array_field() -> None:
    class MyModel(models.Model):
        lst = ArrayField(base_field=models.CharField(max_length=100), null=False)
        null_lst = ArrayField(base_field=models.CharField(max_length=100), null=True)

    assert_type(MyModel().lst, list[str])  # pyrefly: ignore[assert-type]
    # The mypy plugin folds column nullability into `list[str] | None`; plugin-less checkers keep `list[str]`.
    assert_type(MyModel().null_lst, list[str] | None)  # pyright: ignore[reportAssertTypeFailure] # ty: ignore[type-assertion-failure] # pyrefly: ignore[assert-type]

    my_model = MyModel()
    random_uuid = uuid.uuid4()

    my_model.lst = None  # type: ignore[assignment] # pyright: ignore[reportAttributeAccessIssue] # ty: ignore[invalid-assignment] # pyrefly: ignore[bad-argument-type]
    my_model.lst = [random_uuid, random_uuid]  # type: ignore[list-item] # pyright: ignore[reportAttributeAccessIssue] # ty: ignore[invalid-assignment] # pyrefly: ignore[bad-argument-type]
    # Nullable column: mypy accepts None; plugin-less checkers still reject it.
    my_model.null_lst = None  # pyright: ignore[reportAttributeAccessIssue] # ty: ignore[invalid-assignment] # pyrefly: ignore[bad-argument-type]
    my_model.null_lst = [random_uuid, random_uuid]  # type: ignore[list-item] # pyright: ignore[reportAttributeAccessIssue] # ty: ignore[invalid-assignment] # pyrefly: ignore[bad-argument-type]


def array_field_base_field_parsed_into_generic_typevar() -> None:
    class MyModel(models.Model):
        untyped = ArrayField(base_field=models.Field())
        members = ArrayField(base_field=models.IntegerField())
        members_as_text = ArrayField(base_field=models.CharField(max_length=255))

    my_model = MyModel(untyped=[], members=[1, 2], members_as_text=["A", "B"])
    assert_type(my_model.untyped, list[Any])
    assert_type(my_model.members, list[int])  # False positive -> # pyrefly: ignore[assert-type]
    assert_type(my_model.members_as_text, list[str])  # False positive -> # pyrefly: ignore[assert-type]
