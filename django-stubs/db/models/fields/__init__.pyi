import decimal
import uuid
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date, time, timedelta
from datetime import datetime as real_datetime
from typing import Any, ClassVar, Generic, Literal, Protocol, TypeAlias, overload, type_check_only

from django import forms
from django.core import validators  # due to weird mypy.stubtest error
from django.core.checks import CheckMessage
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Model
from django.db.models.expressions import Col, Combinable, Expression, Func
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.db.models.query import _OrderByFieldName
from django.db.models.query_utils import Q, RegisterLookupMixin
from django.db.models.sql.compiler import SQLCompiler, _AsSqlType, _ParamsT
from django.utils.choices import BlankChoiceIterator, _Choice, _ChoiceNamedGroup, _ChoicesCallable, _ChoicesInput
from django.utils.datastructures import DictWrapper
from django.utils.functional import _Getter, _StrOrPromise, cached_property
from typing_extensions import Self, TypeVar, override

class Empty: ...
class NOT_PROVIDED: ...

BLANK_CHOICE_DASH: list[tuple[str, str]]

_ChoicesList: TypeAlias = Sequence[_Choice] | Sequence[_ChoiceNamedGroup]
_LimitChoicesTo: TypeAlias = Q | dict[str, Any]
_LimitChoicesToCallable: TypeAlias = Callable[[], _LimitChoicesTo]

_F = TypeVar("_F", bound=Field[Any, Any], covariant=True)

@type_check_only
class _FieldDescriptor(Protocol[_F]):
    """
    Accessing fields of a model class (not instance) returns an object conforming to this protocol.
    Depending on field type this could be DeferredAttribute, ForwardManyToOneDescriptor, FileDescriptor, etc.
    """

    @property
    def field(self) -> _F: ...

_AllLimitChoicesTo: TypeAlias = _LimitChoicesTo | _LimitChoicesToCallable | _ChoicesCallable  # noqa: PYI047
_ErrorMessagesMapping: TypeAlias = Mapping[str, _StrOrPromise]
_ErrorMessagesDict: TypeAlias = dict[str, _StrOrPromise]

# __set__ value type
_ST = TypeVar("_ST", contravariant=True)
# __get__ return type
_GT = TypeVar("_GT", covariant=True)

_ST_INT = TypeVar("_ST_INT", contravariant=True, default=float | int | str | Combinable)
_GT_INT = TypeVar("_GT_INT", covariant=True, default=int)
_ST_FLOAT = TypeVar("_ST_FLOAT", contravariant=True, default=float | int | str | Combinable)
_GT_FLOAT = TypeVar("_GT_FLOAT", covariant=True, default=float)
_ST_DECIMAL = TypeVar("_ST_DECIMAL", contravariant=True, default=str | float | decimal.Decimal | Combinable)
_GT_DECIMAL = TypeVar("_GT_DECIMAL", covariant=True, default=decimal.Decimal)
_ST_CHAR = TypeVar("_ST_CHAR", contravariant=True, default=str | int | Combinable)
_GT_CHAR = TypeVar("_GT_CHAR", covariant=True, default=str)
_ST_EMAIL = TypeVar("_ST_EMAIL", contravariant=True, default=str | Combinable)
_ST_TEXT = TypeVar("_ST_TEXT", contravariant=True, default=str | Combinable)
_GT_TEXT = TypeVar("_GT_TEXT", covariant=True, default=str)
_ST_BOOL = TypeVar("_ST_BOOL", contravariant=True, default=bool | Combinable)
_GT_BOOL = TypeVar("_GT_BOOL", covariant=True, default=bool)
_ST_NBOOL = TypeVar("_ST_NBOOL", contravariant=True, default=bool | Combinable | None)
_GT_NBOOL = TypeVar("_GT_NBOOL", covariant=True, default=bool | None)
_ST_IP = TypeVar("_ST_IP", contravariant=True, default=str | Combinable)
_GT_IP = TypeVar("_GT_IP", covariant=True, default=str)
_ST_GENIP = TypeVar("_ST_GENIP", contravariant=True, default=str | int | Callable[..., Any] | Combinable)
_ST_DATE = TypeVar("_ST_DATE", contravariant=True, default=str | date | Combinable)
_GT_DATE = TypeVar("_GT_DATE", covariant=True, default=date)
_ST_TIME = TypeVar("_ST_TIME", contravariant=True, default=str | time | real_datetime | Combinable)
_GT_TIME = TypeVar("_GT_TIME", covariant=True, default=time)
_ST_DATETIME = TypeVar("_ST_DATETIME", contravariant=True, default=str | real_datetime | date | Combinable)
_GT_DATETIME = TypeVar("_GT_DATETIME", covariant=True, default=real_datetime)
_ST_UUID = TypeVar("_ST_UUID", contravariant=True, default=str | uuid.UUID)
_GT_UUID = TypeVar("_GT_UUID", covariant=True, default=uuid.UUID)
_ST_BINARY = TypeVar("_ST_BINARY", contravariant=True, default=bytes | bytearray | memoryview | Combinable)
_GT_BINARY = TypeVar("_GT_BINARY", covariant=True, default=bytes | memoryview)
_ST_DURATION = TypeVar("_ST_DURATION", contravariant=True, default=str | timedelta | Combinable)
_GT_DURATION = TypeVar("_GT_DURATION", covariant=True, default=timedelta)
_ST_AUTO = TypeVar("_ST_AUTO", contravariant=True, default=Combinable | int | str)
_GT_AUTO = TypeVar("_GT_AUTO", covariant=True, default=int)

class Field(RegisterLookupMixin, Generic[_ST, _GT]):
    """
    Typing model fields.

    How does this work?
    Let's take a look at the self-contained example
    (it is way easier than our django implementation, but has the same concept).

    To understand this example you need:
    1. Be familiar with descriptors: https://docs.python.org/3/howto/descriptor.html
    2. Follow our explanation below

    Let's start with defining our fake model class and fake integer field.

    .. code:: python

        from typing import Generic

        class Model(object):
            ...

        _SetType = int | float  # You can assign ints and floats
        _GetType = int  # access type is always `int`

        class IntField(object):
            def __get__(self, instance: Model, owner) -> _GetType:
                ...

            def __set__(self, instance, value: _SetType) -> None:
                ...

    Now, let's create our own example model,
    this would be something like ``User`` in your own apps:

    .. code:: python

        class Example(Model):
            count = IntField()

    And now, lets test that our reveal type works:

    .. code:: python

        example = Example()
        reveal_type(example.count)
        # Revealed type is "int"

        example.count = 1.5  # ok
        example.count = 'a'
        # Incompatible types in assignment
        # (expression has type "str", variable has type "int | float")

    Notice, that this is not magic. This is how descriptors work with ``mypy``.

    We also need ``_pyi_lookup_exact_type`` to help inside our plugin.
    It is required to enhance parts like ``filter`` queries.
    """

    _pyi_lookup_exact_type: Any

    help_text: _StrOrPromise
    attname: str
    auto_created: bool
    primary_key: bool
    remote_field: ForeignObjectRel | None
    is_relation: bool
    related_model: type[Model] | Literal["self"] | None
    generated: ClassVar[bool]
    one_to_many: bool | None
    one_to_one: bool | None
    many_to_many: bool | None
    many_to_one: bool | None
    max_length: int | None
    model: type[Model]
    name: str
    verbose_name: _StrOrPromise
    description: _StrOrPromise | _Getter[_StrOrPromise]
    blank: bool
    null: bool
    editable: bool
    empty_strings_allowed: bool
    choices: _ChoicesList | None
    db_column: str | None
    db_comment: str | None
    db_default: type[NOT_PROVIDED] | Expression
    column: str | None
    concrete: bool
    default: Any
    empty_values: Sequence[Any]
    creation_counter: int
    auto_creation_counter: int
    default_validators: Sequence[validators._ValidatorCallable]
    default_error_messages: ClassVar[_ErrorMessagesDict]
    hidden: bool
    system_check_removed_details: Any | None
    system_check_deprecated_details: Any | None
    non_db_attrs: tuple[str, ...]
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        primary_key: bool = False,
        max_length: int | None = None,
        unique: bool = False,
        blank: bool = False,
        null: bool = False,
        db_index: bool = False,
        rel: ForeignObjectRel | None = None,
        default: Any = ...,
        editable: bool = True,
        serialize: bool = True,
        unique_for_date: str | None = None,
        unique_for_month: str | None = None,
        unique_for_year: str | None = None,
        choices: _ChoicesInput | None = None,
        help_text: _StrOrPromise = "",
        db_column: str | None = None,
        db_tablespace: str | None = None,
        auto_created: bool = False,
        validators: Iterable[validators._ValidatorCallable] = (),
        error_messages: _ErrorMessagesMapping | None = None,
        db_comment: str | None = None,
        db_default: type[NOT_PROVIDED] | Expression | _ST = ...,
    ) -> None: ...
    def __set__(self, instance: Any, value: _ST) -> None: ...
    # class access
    @overload
    def __get__(self, instance: None, owner: Any) -> _FieldDescriptor[Self]: ...
    # Model instance access
    @overload
    def __get__(self, instance: Model, owner: Any) -> _GT: ...
    # non-Model instances
    @overload
    def __get__(self, instance: Any, owner: Any) -> Self: ...
    def check(self, **kwargs: Any) -> list[CheckMessage]: ...
    def get_col(self, alias: str, output_field: Field | None = None) -> Col: ...
    @cached_property
    def cached_col(self) -> Col: ...
    def select_format(self, compiler: SQLCompiler, sql: str, params: _ParamsT) -> _AsSqlType: ...
    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]: ...
    def clone(self) -> Self: ...
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __deepcopy__(self, memodict: dict[int, Any]) -> Self: ...
    def __copy__(self) -> Self: ...
    def get_pk_value_on_save(self, instance: Model) -> Any: ...
    def to_python(self, value: Any) -> Any: ...
    @cached_property
    def error_messages(self) -> _ErrorMessagesDict: ...
    @cached_property
    def validators(self) -> list[validators._ValidatorCallable]: ...
    def run_validators(self, value: Any) -> None: ...
    def validate(self, value: Any, model_instance: Model | None) -> None: ...
    def clean(self, value: Any, model_instance: Model | None) -> Any: ...
    def db_type_parameters(self, connection: BaseDatabaseWrapper) -> DictWrapper: ...
    def db_check(self, connection: BaseDatabaseWrapper) -> str | None: ...
    def db_type(self, connection: BaseDatabaseWrapper) -> str | None: ...
    def rel_db_type(self, connection: BaseDatabaseWrapper) -> str | None: ...
    def cast_db_type(self, connection: BaseDatabaseWrapper) -> str | None: ...
    def db_parameters(self, connection: BaseDatabaseWrapper) -> dict[str, str | None]: ...
    def db_type_suffix(self, connection: BaseDatabaseWrapper) -> str | None: ...
    def get_db_converters(self, connection: BaseDatabaseWrapper) -> list[Callable[..., Any]]: ...
    @cached_property
    def unique(self) -> bool: ...
    @property
    def db_tablespace(self) -> str: ...
    @property
    def db_returning(self) -> bool: ...
    descriptor_class: type
    def set_attributes_from_name(self, name: str) -> None: ...
    def contribute_to_class(self, cls: type[Model], name: str, private_only: bool = False) -> None: ...
    def get_filter_kwargs_for_object(self, obj: Model) -> dict[str, Any]: ...
    def get_attname(self) -> str: ...
    def get_attname_column(self) -> tuple[str, str | None]: ...
    def get_internal_type(self) -> str: ...
    def pre_save(self, model_instance: Model, add: bool) -> Any: ...
    def get_prep_value(self, value: Any) -> Any: ...
    def get_db_prep_value(self, value: Any, connection: BaseDatabaseWrapper, prepared: bool = False) -> Any: ...
    def get_db_prep_save(self, value: Any, connection: BaseDatabaseWrapper) -> Any: ...
    def has_default(self) -> bool: ...
    def has_db_default(self) -> bool: ...
    def get_default(self) -> Any: ...
    def get_choices(
        self,
        include_blank: bool = True,
        blank_choice: _ChoicesList = ...,
        limit_choices_to: _LimitChoicesTo | None = None,
        ordering: Sequence[_OrderByFieldName] = (),
    ) -> BlankChoiceIterator | _ChoicesList: ...
    def value_to_string(self, obj: Model) -> str: ...
    @property
    def flatchoices(self) -> list[_Choice]: ...
    def save_form_data(self, instance: Model, data: Any) -> None: ...
    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field | None: ...
    def value_from_object(self, obj: Model) -> _GT: ...
    def slice_expression(self, expression: Expression, start: int, length: int | None) -> Func: ...

class IntegerField(Field[_ST_INT, _GT_INT]):
    _pyi_lookup_exact_type: str | int
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class PositiveIntegerRelDbTypeMixin:
    def rel_db_type(self, connection: BaseDatabaseWrapper) -> str: ...

class SmallIntegerField(IntegerField[_ST_INT, _GT_INT]): ...

class BigIntegerField(IntegerField[_ST_INT, _GT_INT]):
    MAX_BIGINT: ClassVar[int]
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class PositiveIntegerField(PositiveIntegerRelDbTypeMixin, IntegerField[_ST_INT, _GT_INT]):
    integer_field_class: type[IntegerField]
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class PositiveSmallIntegerField(PositiveIntegerRelDbTypeMixin, SmallIntegerField[_ST_INT, _GT_INT]):
    integer_field_class: type[SmallIntegerField]
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class PositiveBigIntegerField(PositiveIntegerRelDbTypeMixin, BigIntegerField[_ST_INT, _GT_INT]):
    integer_field_class: type[BigIntegerField]
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class FloatField(Field[_ST_FLOAT, _GT_FLOAT]):
    _pyi_lookup_exact_type: float
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class DecimalField(Field[_ST_DECIMAL, _GT_DECIMAL]):
    _pyi_lookup_exact_type: str | int | decimal.Decimal
    # attributes
    max_digits: int
    decimal_places: int
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        *,
        primary_key: bool = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_DECIMAL = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @cached_property
    def context(self) -> decimal.Context: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class CharField(Field[_ST_CHAR, _GT_CHAR]):
    # objects are converted to string before comparison
    _pyi_lookup_exact_type: Any
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_CHAR = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
        *,
        db_collation: str | None = None,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class CommaSeparatedIntegerField(CharField[_ST_CHAR, _GT_CHAR]): ...

class SlugField(CharField[_ST_CHAR, _GT_CHAR]):
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        primary_key: bool = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_CHAR = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
        *,
        max_length: int | None = 50,
        db_index: bool = True,
        allow_unicode: bool = False,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class EmailField(CharField[_ST_EMAIL, _GT_CHAR]):
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class URLField(CharField[_ST_CHAR, _GT_CHAR]):
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        *,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        rel: ForeignObjectRel | None = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_CHAR = ...,
        editable: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        auto_created: bool = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class TextField(Field[_ST_TEXT, _GT_TEXT]):
    # objects are converted to string before comparison
    _pyi_lookup_exact_type: Any
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_TEXT = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
        *,
        db_collation: str | None = None,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class BooleanField(Field[_ST_BOOL, _GT_BOOL]):
    _pyi_lookup_exact_type: bool
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class NullBooleanField(BooleanField[_ST_NBOOL, _GT_NBOOL]):
    _pyi_lookup_exact_type: bool | None  # type: ignore[assignment]

class IPAddressField(Field[_ST_IP, _GT_IP]): ...

class GenericIPAddressField(Field[_ST_GENIP, _GT_IP]):
    default_error_messages: ClassVar[_ErrorMessagesDict]
    unpack_ipv4: bool
    protocol: str
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: Any | None = None,
        protocol: str = "both",
        unpack_ipv4: bool = False,
        primary_key: bool = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_GENIP = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class DateTimeCheckMixin:
    def check(self, **kwargs: Any) -> list[CheckMessage]: ...

class DateField(DateTimeCheckMixin, Field[_ST_DATE, _GT_DATE]):
    _pyi_lookup_exact_type: str | date
    auto_now: bool
    auto_now_add: bool
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        auto_now: bool = False,
        auto_now_add: bool = False,
        *,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_DATE = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def contribute_to_class(self, cls: type[Model], name: str, **kwargs: Any) -> None: ...  # type: ignore[override]
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class TimeField(DateTimeCheckMixin, Field[_ST_TIME, _GT_TIME]):
    auto_now: bool
    auto_now_add: bool
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        auto_now: bool = False,
        auto_now_add: bool = False,
        *,
        primary_key: bool = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_TIME = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class DateTimeField(DateField[_ST_DATETIME, _GT_DATETIME]):
    _pyi_lookup_exact_type: str | real_datetime
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class UUIDField(Field[_ST_UUID, _GT_UUID]):
    _pyi_lookup_exact_type: uuid.UUID | str
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        *,
        name: str | None = ...,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        rel: ForeignObjectRel | None = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST_UUID = ...,
        editable: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        auto_created: bool = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class FilePathField(Field[_ST, _GT]):
    path: Any
    match: str | None
    recursive: bool
    allow_files: bool
    allow_folders: bool
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        path: str | Callable[..., str] = "",
        match: str | None = None,
        recursive: bool = False,
        allow_files: bool = True,
        allow_folders: bool = False,
        *,
        primary_key: bool = ...,
        max_length: int = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        choices: _ChoicesInput | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[validators._ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class BinaryField(Field[_ST_BINARY, _GT_BINARY]):
    def get_placeholder(self, value: Any, compiler: SQLCompiler, connection: BaseDatabaseWrapper) -> str: ...

class DurationField(Field[_ST_DURATION, _GT_DURATION]):
    @override
    def formfield(self, **kwargs: Any) -> forms.Field | None: ...  # type: ignore[override]

class AutoFieldMixin:
    db_returning: bool
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def check(self, **kwargs: Any) -> list[CheckMessage]: ...
    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]: ...
    def validate(self, value: Any, model_instance: Model | None) -> None: ...
    def get_db_prep_value(self, value: Any, connection: BaseDatabaseWrapper, prepared: bool = False) -> Any: ...
    def contribute_to_class(self, cls: type[Model], name: str, **kwargs: Any) -> None: ...
    def formfield(self, **kwargs: Any) -> None: ...

class AutoFieldMeta(type): ...

class AutoField(AutoFieldMixin, IntegerField[_ST_AUTO, _GT_AUTO], metaclass=AutoFieldMeta):  # type: ignore[misc]
    _pyi_lookup_exact_type: str | int

class BigAutoField(AutoFieldMixin, BigIntegerField[_ST_AUTO, _GT_AUTO]): ...  # type: ignore[misc]
class SmallAutoField(AutoFieldMixin, SmallIntegerField[_ST_AUTO, _GT_AUTO]): ...  # type: ignore[misc]

__all__ = [
    "BLANK_CHOICE_DASH",
    "NOT_PROVIDED",
    "AutoField",
    "BigAutoField",
    "BigIntegerField",
    "BinaryField",
    "BooleanField",
    "CharField",
    "CommaSeparatedIntegerField",
    "DateField",
    "DateTimeField",
    "DecimalField",
    "DurationField",
    "EmailField",
    "Empty",
    "Field",
    "FilePathField",
    "FloatField",
    "GenericIPAddressField",
    "IPAddressField",
    "IntegerField",
    "NullBooleanField",
    "PositiveBigIntegerField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
    "SlugField",
    "SmallAutoField",
    "SmallIntegerField",
    "TextField",
    "TimeField",
    "URLField",
    "UUIDField",
]
