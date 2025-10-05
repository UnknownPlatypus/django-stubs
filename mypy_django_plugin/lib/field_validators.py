from abc import ABC, abstractmethod
from typing import final

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field
from django.db.models.base import Model
from mypy.plugin import MethodContext


class FieldValidator(ABC):
    """Base field arguments validator for QuerySet methods"""

    __slots__ = ("ctx", "field_name", "method", "opts")

    def __init__(self, ctx: MethodContext, model_cls: type[Model], field_name: str, method: str):
        self.ctx = ctx
        self.opts = model_cls._meta
        self.field_name = field_name if field_name != "pk" else self.opts.pk.name
        self.method = method

    def _get_field(self) -> Field | None:
        """Lookup the field by name."""
        try:
            return self.opts.get_field(self.field_name)
        except FieldDoesNotExist as e:
            self.ctx.api.fail(str(e), self.ctx.context)
            return None

    def _check_concrete(self, field: Field) -> bool:
        """Check if the field is concrete."""
        if not field.concrete or field.many_to_many:
            self.ctx.api.fail(
                f'"{self.method}()" can only be used with concrete fields. Got "{self.field_name}"', self.ctx.context
            )
            return False
        return True

    def _check_not_pk(self, field: Field, custom_message: str | None = None) -> bool:
        """Check if field is not a primary key."""
        all_pk_fields = set(self.opts.pk_fields)
        for parent in self.opts.all_parents:
            all_pk_fields.update(parent._meta.pk_fields)

        if field in all_pk_fields:
            message = (
                custom_message or f'"{self.method}()" cannot be used with primary key fields. Got "{self.field_name}"'
            )
            self.ctx.api.fail(message, self.ctx.context)
            return False
        return True

    @abstractmethod
    def extra_checks(self, field: Field) -> bool:
        """Override to define validation checks. Return False to fail validation."""
        return True

    @final
    def validate(self) -> bool:
        """Run all validations."""
        if (field := self._get_field()) is None:
            return False
        return self.extra_checks(field)


class BulkUpdateFieldValidator(FieldValidator):
    """Ensure fields passed to `bulk_update(..., fields=...)` are valid in this context."""

    def extra_checks(self, field: Field) -> bool:
        return self._check_concrete(field) and self._check_not_pk(field)


class BulkCreateUpdateFieldValidator(FieldValidator):
    """Ensure fields passed to `bulk_create(..., update_fields=...)` are valid in this context."""

    def extra_checks(self, field: Field) -> bool:
        return self._check_concrete(field) and self._check_not_pk(
            field, f'"{self.method}()" cannot be used with primary key fields in update_fields. Got "{self.field_name}"'
        )


class BulkCreateUniqueFieldValidator(FieldValidator):
    """Ensure fields passed to `bulk_create(..., unique_fields=...)` are valid in this context."""

    def extra_checks(self, field: Field) -> bool:
        return self._check_concrete(field)
