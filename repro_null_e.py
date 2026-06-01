"""Option E: __init__ overloads on base Field with Any self-types only.

Idea: option B uses `self: Field[_ST, _GT, Literal[X]]` which pyright rejects
(reportInvalidTypeVarUse — _ST/_GT not bound from elsewhere). Replace with
`self: Field[Any, Any, Literal[X]]` so only _NT is constrained. _ST/_GT are
bound via the class-level subscription on each subclass declaration.
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
    def __init__(self: Field[Any, Any, Literal[False]], *, null: Literal[False] = False, **kwargs: Any) -> None: ...
    @overload
    def __init__(self: Field[Any, Any, Literal[True]], *, null: Literal[True], **kwargs: Any) -> None: ...
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
    @overload
    def __init__(
        self: CharField[Any, Any, Literal[False]],
        *,
        max_length: int | None = None,
        null: Literal[False] = False,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self: CharField[Any, Any, Literal[True]],
        *,
        max_length: int | None = None,
        null: Literal[True],
        **kwargs: Any,
    ) -> None: ...
    def __init__(self, **kwargs: Any) -> None: ...


_ST_Int = TypeVar("_ST_Int", contravariant=True, default=float | int | str)
_GT_Int = TypeVar("_GT_Int", covariant=True, default=int)


class IntegerField(Field[_ST_Int, _GT_Int, _NT]):
    @overload
    def __init__(
        self: IntegerField[Any, Any, Literal[False]],
        *,
        null: Literal[False] = False,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self: IntegerField[Any, Any, Literal[True]],
        *,
        null: Literal[True],
        **kwargs: Any,
    ) -> None: ...
    def __init__(self, **kwargs: Any) -> None: ...


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


def takes_field(f: Field[str, str]) -> None:
    reveal_type(f)
