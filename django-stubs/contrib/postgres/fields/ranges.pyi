from typing import Any, Literal

from django.db import models
from django.db.models.lookups import PostgresOperatorLookup
from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange, Range

class RangeBoundary(models.Expression):
    lower: str
    upper: str
    def __init__(self, inclusive_lower: bool = ..., inclusive_upper: bool = ...) -> None: ...

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

class RangeField(models.Field):
    empty_strings_allowed: bool
    base_field: models.Field
    range_type: type[Range]
    def get_prep_value(self, value: Any) -> Any | None: ...
    def to_python(self, value: Any) -> Any: ...

class IntegerRangeField(RangeField):
    def __get__(self, instance: Any, owner: Any) -> NumericRange: ...

class BigIntegerRangeField(RangeField):
    def __get__(self, instance: Any, owner: Any) -> NumericRange: ...

class DecimalRangeField(RangeField):
    def __get__(self, instance: Any, owner: Any) -> NumericRange: ...

class DateTimeRangeField(RangeField):
    def __get__(self, instance: Any, owner: Any) -> DateTimeTZRange: ...

class DateRangeField(RangeField):
    def __get__(self, instance: Any, owner: Any) -> DateRange: ...

class DateTimeRangeContains(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class RangeContainedBy(PostgresOperatorLookup):
    lookup_name: str
    type_mapping: dict[str, str]
    postgres_operator: str

class FullyLessThan(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class FullGreaterThan(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class NotLessThan(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class NotGreaterThan(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class AdjacentToLookup(PostgresOperatorLookup):
    lookup_name: str
    postgres_operator: str

class RangeStartsWith(models.Transform):
    @property
    def output_field(self) -> models.Field: ...  # type: ignore[override]

class RangeEndsWith(models.Transform):
    @property
    def output_field(self) -> models.Field: ...  # type: ignore[override]

class IsEmpty(models.Transform):
    output_field: models.BooleanField  # type: ignore[assignment]

class LowerInclusive(models.Transform):
    output_field: models.BooleanField  # type: ignore[assignment]

class LowerInfinite(models.Transform):
    output_field: models.BooleanField  # type: ignore[assignment]

class UpperInclusive(models.Transform):
    output_field: models.BooleanField  # type: ignore[assignment]

class UpperInfinite(models.Transform):
    output_field: models.BooleanField  # type: ignore[assignment]
