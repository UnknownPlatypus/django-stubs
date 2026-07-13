from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import TypedDict, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from django.core.validators import _ValidatorCallable
    from django.db.models.expressions import Expression
    from django.db.models.fields import NOT_PROVIDED
    from django.db.models.fields.reverse_related import ForeignObjectRel
    from django.utils.choices import _ChoicesInput
    from django.utils.functional import _StrOrPromise

# The type accepted by `db_default`, i.e. the field's set type. Nullable constructor
# overloads substitute their concrete `... | None` union here.
_DB = TypeVar("_DB", default=Any)


class FieldInitKwargs(TypedDict, Generic[_DB], total=False, closed=True):
    """Keyword arguments understood by every `models.Field` constructor.

    Use it to declare `__init__` overloads on a custom field without spelling out
    the full argument list, keeping keyword argument checking:

        **kwargs: Unpack[FieldInitKwargs[str | None]]

    `closed=True` is load-bearing: it makes ty reject unknown keys passed through
    `**kwargs` (mypy/pyright/pyrefly reject them for open TypedDicts already).
    """

    primary_key: bool
    max_length: int | None
    unique: bool
    blank: bool
    db_index: bool
    rel: ForeignObjectRel | None
    default: Any
    editable: bool
    serialize: bool
    unique_for_date: str | None
    unique_for_month: str | None
    unique_for_year: str | None
    choices: _ChoicesInput | None
    help_text: _StrOrPromise
    db_column: str | None
    db_tablespace: str | None
    auto_created: bool
    validators: Iterable[_ValidatorCallable]
    error_messages: Mapping[str, _StrOrPromise] | None
    db_comment: str | None
    db_default: type[NOT_PROVIDED] | Expression | _DB


__all__ = ["FieldInitKwargs"]
