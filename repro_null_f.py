"""Option F: __new__ overloads on the BASE Field class only.

Idea: option C needs __new__ on every subclass. Move them up to Field so
subclasses inherit. Subclass `__init__` still declares its own kwargs (no
overload), but the inherited `__new__` does the binding.
"""

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
    @overload
    def __new__(cls, *, null: Literal[False] = False, **kwargs: Any) -> Field[_ST, _GT, Literal[False]]: ...
    @overload
    def __new__(cls, *, null: Literal[True], **kwargs: Any) -> Field[_ST, _GT, Literal[True]]: ...
    def __new__(cls, **kwargs: Any) -> Field[Any, Any, Any]:
        return object.__new__(cls)

    def __init__(self, **kwargs: Any) -> None: ...

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
    def __init__(self, *, max_length: int | None = None, **kwargs: Any) -> None: ...


_ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
_GT_Int = TypeVar("_GT_Int", covariant=True, default=int)


class IntegerField(Field[_ST_Int, _GT_Int, _NT]):
    def __init__(self, **kwargs: Any) -> None: ...


# Simulating a user-defined custom subclass — no __new__ override.
class MyCustomCharField(CharField[_ST_Char, _GT_Char, _NT]):
    pass


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

book.subtitle = None  # OK
book.edition = None
book.isbn = None  # expect: error
book.title = None  # expect: error
book.pages = None  # expect: error
book.custom_a = None  # expect: error
book.custom_b = None  # OK

dyn = CharField(max_length=10, null=bool(random.random()))
reveal_type(dyn)


def takes_field(f: Field[str, str]) -> None:
    reveal_type(f)
