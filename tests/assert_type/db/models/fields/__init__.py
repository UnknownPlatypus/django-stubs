from django.db.models import Field, TextField
from django.utils.functional import _StrOrPromise
from django.utils.translation import gettext_lazy as _
from typing_extensions import assert_type

assert_type(Field().description, _StrOrPromise)  # Declared with a property
assert_type(TextField().description, _StrOrPromise)  # Declared with a class variable


# Check overrides of Field.description (that is a property)
class MyField1(Field[int, int]):
    description = "aaaa"


class MyField2(Field[int, int]):
    description = _("aaaa")


class MyField3(Field[int, int]):
    @property
    def description(self) -> _StrOrPromise:
        return "aaaa"


class MyField4(Field[int, int]):
    @property
    def description(self) -> _StrOrPromise:
        return _("aaaa")


# Check overrides of TextField.description (that is a classvariable)
class MyTextField1(TextField[str, str]):
    description = "aaaa"


class MyTextField2(TextField[str, str]):
    description = _("aaaa")


class MyTextField3(TextField[str, str]):
    @property
    def description(self) -> _StrOrPromise:
        return "aaaa"


class MyTextField4(TextField[str, str]):
    @property
    def description(self) -> _StrOrPromise:
        return _("aaaa")
