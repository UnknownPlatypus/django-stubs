from collections.abc import Sequence
from typing import Any, ClassVar

from _typeshed import Unused
from django.contrib.postgres.utils import CheckPostgresInstalledMixin
from django.core.checks import CheckMessage
from django.core.validators import _ValidatorCallable
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Field
from django.db.models.expressions import Combinable
from django.db.models.fields import _ErrorMessagesDict
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.db.models.lookups import Transform
from django.db.models.sql.compiler import _AsSqlType
from django.utils.functional import _StrOrPromise
from typing_extensions import TypeVar, Unpack, override

from django_stubs_ext import FieldInitKwargs

_ST_Array = TypeVar("_ST_Array", contravariant=True, default=Any)
_GT_Array = TypeVar("_GT_Array", covariant=True, default=Any)

class ArrayField(
    CheckPostgresInstalledMixin, CheckFieldDefaultMixin, Field[Sequence[_ST_Array] | Combinable, list[_GT_Array]]
):
    empty_strings_allowed: bool
    default_error_messages: ClassVar[_ErrorMessagesDict]
    base_field: Field[_ST_Array, _GT_Array]
    size: int | None
    default_validators: list[_ValidatorCallable]
    from_db_value: Any
    def __init__(
        self,
        base_field: Field[_ST_Array, _GT_Array],
        size: int | None = None,
        *,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        null: bool = False,
        **kwargs: Unpack[FieldInitKwargs[Sequence[_ST_Array]]],
    ) -> None: ...
    @override
    def check(self, **kwargs: Any) -> list[CheckMessage]: ...
    @property
    @override
    def description(self) -> str: ...  # type: ignore[override]
    @override
    def cast_db_type(self, connection: BaseDatabaseWrapper) -> str: ...
    def get_placeholder_sql(self, value: Unused, compiler: Unused, connection: BaseDatabaseWrapper) -> _AsSqlType: ...
    @override
    def get_transform(self, name: str) -> type[Transform] | None: ...

__all__ = ["ArrayField"]
