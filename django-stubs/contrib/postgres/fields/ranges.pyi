from typing import Any, ClassVar, Literal, overload

from _typeshed import Unused
from django.contrib.postgres import forms
from django.contrib.postgres.utils import CheckPostgresInstalledMixin
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models.fields import FieldInitKwargs
from django.db.models.lookups import PostgresOperatorLookup
from django.db.models.sql.compiler import SQLCompiler, _AsSqlType
from django.utils.functional import _StrOrPromise
from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange, Range
from typing_extensions import TypeVar, Unpack, override

class RangeBoundary(models.Expression):
    lower: str
    upper: str
    def __init__(self, inclusive_lower: bool = True, inclusive_upper: bool = False) -> None: ...

class RangeOperators:
    EQUAL: Literal["="]
    NOT_EQUAL: Literal["<>"]
    CONTAINS: Literal["@>"]
    CONTAINED_BY: Literal["<@"]
    OVERLAPS: Literal["&&"]
    FULLY_LT: Literal["<<"]
    FULLY_GT: Literal[">>"]
    NOT_LT: Literal["&>"]
    NOT_GT: Literal["&<"]
    ADJACENT_TO: Literal["-|-"]

_RangeT = TypeVar("_RangeT", bound=Range[Any] | None)
_NumericRangeT = TypeVar("_NumericRangeT", bound=NumericRange | None, default=NumericRange)
_DateTimeRangeT = TypeVar("_DateTimeRangeT", bound=DateTimeTZRange | None, default=DateTimeTZRange)
_DateRangeT = TypeVar("_DateRangeT", bound=DateRange | None, default=DateRange)

class RangeField(CheckPostgresInstalledMixin, models.Field[Any, _RangeT]):
    empty_strings_allowed: bool
    base_field: type[models.Field]
    range_type: type[_RangeT]
    def get_placeholder_sql(self, value: Unused, compiler: Unused, connection: BaseDatabaseWrapper) -> _AsSqlType: ...
    @override
    def get_prep_value(self, value: Any) -> Any | None: ...
    @override
    def to_python(self, value: Any) -> Any: ...
    @override
    def value_to_string(self, obj: models.Model) -> str | None: ...  # type: ignore[override]

class ContinuousRangeField(RangeField[_RangeT]):
    default_bounds: str
    def __init__(self, *args: Any, default_bounds: str = "[)", **kwargs: Any) -> None: ...

class IntegerRangeField(RangeField[_NumericRangeT]):
    base_field: type[models.IntegerField]
    form_field: type[forms.IntegerRangeField]
    @overload
    def __init__(  # nullable: read and write accept None
        self: IntegerRangeField[NumericRange | None],
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: Literal[True],
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...
    @overload
    def __init__(  # fallback: dynamic flags keep the class defaults
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: bool = False,
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...

class BigIntegerRangeField(RangeField[_NumericRangeT]):
    base_field: type[models.BigIntegerField]
    form_field: type[forms.IntegerRangeField]
    @overload
    def __init__(  # nullable: read and write accept None
        self: BigIntegerRangeField[NumericRange | None],
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: Literal[True],
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...
    @overload
    def __init__(  # fallback: dynamic flags keep the class defaults
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: bool = False,
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...

class DecimalRangeField(ContinuousRangeField[_NumericRangeT]):
    base_field: type[models.DecimalField]
    form_field: type[forms.DecimalRangeField]
    @overload
    def __init__(  # nullable: read and write accept None
        self: DecimalRangeField[NumericRange | None],
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: Literal[True],
        default_bounds: str = "[)",
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...
    @overload
    def __init__(  # fallback: dynamic flags keep the class defaults
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: bool = False,
        default_bounds: str = "[)",
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...

class DateTimeRangeField(ContinuousRangeField[_DateTimeRangeT]):
    base_field: type[models.DateTimeField]
    form_field: type[forms.DateTimeRangeField]
    @overload
    def __init__(  # nullable: read and write accept None
        self: DateTimeRangeField[DateTimeTZRange | None],
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: Literal[True],
        default_bounds: str = "[)",
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...
    @overload
    def __init__(  # fallback: dynamic flags keep the class defaults
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: bool = False,
        default_bounds: str = "[)",
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...

class DateRangeField(RangeField[_DateRangeT]):
    base_field: type[models.DateField]
    form_field: type[forms.DateRangeField]
    @overload
    def __init__(  # nullable: read and write accept None
        self: DateRangeField[DateRange | None],
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: Literal[True],
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...
    @overload
    def __init__(  # fallback: dynamic flags keep the class defaults
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        null: bool = False,
        **kwargs: Unpack[FieldInitKwargs[Any]],
    ) -> None: ...

class DateTimeRangeContains(PostgresOperatorLookup): ...

class RangeContainedBy(PostgresOperatorLookup):
    type_mapping: dict[str, str]
    @override
    def process_lhs(self, compiler: SQLCompiler, connection: BaseDatabaseWrapper) -> _AsSqlType: ...  # type: ignore[override]

class FullyLessThan(PostgresOperatorLookup): ...
class FullGreaterThan(PostgresOperatorLookup): ...
class NotLessThan(PostgresOperatorLookup): ...
class NotGreaterThan(PostgresOperatorLookup): ...
class AdjacentToLookup(PostgresOperatorLookup): ...

class RangeStartsWith(models.Transform):
    @property
    @override
    def output_field(self) -> models.Field: ...

class RangeEndsWith(models.Transform):
    @property
    @override
    def output_field(self) -> models.Field: ...

class IsEmpty(models.Transform):
    output_field: ClassVar[models.BooleanField]

class LowerInclusive(models.Transform):
    output_field: ClassVar[models.BooleanField]

class LowerInfinite(models.Transform):
    output_field: ClassVar[models.BooleanField]

class UpperInclusive(models.Transform):
    output_field: ClassVar[models.BooleanField]

class UpperInfinite(models.Transform):
    output_field: ClassVar[models.BooleanField]

__all__ = [
    "BigIntegerRangeField",
    "DateRangeField",
    "DateTimeRangeField",
    "DecimalRangeField",
    "IntegerRangeField",
    "RangeBoundary",
    "RangeField",
    "RangeOperators",
]
