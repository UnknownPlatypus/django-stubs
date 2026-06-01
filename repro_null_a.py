"""Option A: drop the third fallback __set__ overload. _NT default stays Any."""

from __future__ import annotations

import random
from typing import Any, Generic, Literal, TypeVar, overload

from typing_extensions import Self, reveal_type


class Model: ...


class Combinable: ...


_ST = TypeVar("_ST", contravariant=True)
_GT = TypeVar("_GT", covariant=True)
_NT = TypeVar("_NT", Literal[True], Literal[False], default=Any)  # type: ignore[misc]


class Field(Generic[_ST, _GT, _NT]):
    def __init__(self, *, null: _NT = False, **kwargs: Any) -> None: ...  # type: ignore[assignment]

    # NO fallback overload — only the two Literal-constrained ones.
    @overload
    def __set__(self: Field[Any, Any, Literal[False]], instance: Any, value: _ST | Combinable) -> None: ...
    @overload
    def __set__(self: Field[Any, Any, Literal[True]], instance: Any, value: _ST | Combinable | None) -> None: ...
    def __set__(self, instance: Any, value: Any) -> None: ...

    @overload
    def __get__(self, instance: None, owner: Any) -> Self: ...
    @overload
    def __get__(self: Field[Any, Any, Literal[False]], instance: Model, owner: Any) -> _GT: ...
    @overload
    def __get__(self: Field[Any, Any, Literal[True]], instance: Model, owner: Any) -> _GT | None: ...
    @overload
    def __get__(self, instance: Any, owner: Any) -> Self: ...
    def __get__(self, instance: Any, owner: Any) -> Any: ...


_ST_Char = TypeVar("_ST_Char", contravariant=True, default=str | int)
_GT_Char = TypeVar("_GT_Char", covariant=True, default=str)


class CharField(Field[_ST_Char, _GT_Char, _NT]):
    def __init__(self, *, max_length: int | None = None, null: _NT = False, **kwargs: Any) -> None: ...  # type: ignore[assignment]


_ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
_GT_Int = TypeVar("_GT_Int", covariant=True, default=int)


class IntegerField(Field[_ST_Int, _GT_Int, _NT]):
    def __init__(self, *, null: _NT = False, **kwargs: Any) -> None: ...  # type: ignore[assignment]


class Book(Model):
    title = CharField(max_length=100)
    pages = IntegerField()
    isbn = CharField(max_length=20, null=False)
    subtitle = CharField(max_length=100, null=True)
    edition = IntegerField(null=True)


book = Book()

reveal_type(book.title)
reveal_type(book.pages)
reveal_type(book.isbn)
reveal_type(book.subtitle)
reveal_type(book.edition)

book.subtitle = None  # OK
book.edition = None  # OK
book.isbn = None  # expect: error
book.title = None  # expect: error (KEY TEST — implicit null=False)
book.pages = None  # expect: error (KEY TEST — implicit null=False)

dyn = CharField(max_length=10, null=bool(random.random()))
reveal_type(dyn)


def takes_field(f: Field[str, str]) -> None:  # bare 2-arg annotation
    reveal_type(f)
