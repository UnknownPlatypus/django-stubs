"""Option C: __new__ overloads on subclasses bind _NT. Field keeps _NT typevar."""

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

    @overload
    def __set__(self: Field[Any, Any, Literal[False]], instance: Any, value: _ST | Combinable) -> None: ...
    @overload
    def __set__(self: Field[Any, Any, Literal[True]], instance: Any, value: _ST | Combinable | None) -> None: ...
    @overload
    def __set__(self, instance: Any, value: _ST | Combinable) -> None: ...
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
    @overload
    def __new__(
        cls, *, max_length: int | None = None, null: Literal[False] = False, **kwargs: Any
    ) -> CharField[_ST_Char, _GT_Char, Literal[False]]: ...
    @overload
    def __new__(
        cls, *, max_length: int | None = None, null: Literal[True], **kwargs: Any
    ) -> CharField[_ST_Char, _GT_Char, Literal[True]]: ...
    def __new__(cls, **kwargs: Any) -> CharField[Any, Any, Any]:
        return object.__new__(cls)


_ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
_GT_Int = TypeVar("_GT_Int", covariant=True, default=int)


class IntegerField(Field[_ST_Int, _GT_Int, _NT]):
    @overload
    def __new__(
        cls, *, null: Literal[False] = False, **kwargs: Any
    ) -> IntegerField[_ST_Int, _GT_Int, Literal[False]]: ...
    @overload
    def __new__(cls, *, null: Literal[True], **kwargs: Any) -> IntegerField[_ST_Int, _GT_Int, Literal[True]]: ...
    def __new__(cls, **kwargs: Any) -> IntegerField[Any, Any, Any]:
        return object.__new__(cls)


class MyCustomCharField(CharField[_ST_Char, _GT_Char, _NT]):
    """User-defined subclass — no __new__ override."""


class Book(Model):
    title = CharField(max_length=100)
    pages = IntegerField()
    isbn = CharField(max_length=20, null=False)
    subtitle = CharField(max_length=100, null=True)
    edition = IntegerField(null=True)
    custom_a = MyCustomCharField(max_length=10)
    custom_b = MyCustomCharField(max_length=10, null=True)


book = Book()

reveal_type(book.title)
reveal_type(book.pages)
reveal_type(book.isbn)
reveal_type(book.subtitle)
reveal_type(book.edition)
reveal_type(book.custom_a)  # expect: str
reveal_type(book.custom_b)  # expect: str | None

book.subtitle = None
book.edition = None
book.isbn = None
book.title = None
book.pages = None
book.custom_a = None  # expect: error (inherited from parent's __new__)
book.custom_b = None  # OK

dyn = CharField(max_length=10, null=bool(random.random()))
reveal_type(dyn)


def takes_field(f: Field[str, str]) -> None:
    reveal_type(f)
