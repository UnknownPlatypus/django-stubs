from django.db.models import Field, SlugField
from django.utils.functional import _StrOrPromise
from django.utils.translation import gettext_lazy as _
from typing_extensions import assert_type

assert_type(Field.description, _StrOrPromise)
assert_type(SlugField.description, _StrOrPromise)
assert_type(Field().description, _StrOrPromise)
assert_type(SlugField().description, _StrOrPromise)


# Check various allowed override of Field.description
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


class MySlugField1(SlugField[str, str]):
    description = "aaaa"


class MySlugField2(SlugField[str, str]):
    description = _("aaaa")


class MySlugField3(SlugField[str, str]):
    @property
    def description(self) -> _StrOrPromise:
        return "aaaa"


class MySlugField4(SlugField[str, str]):
    @property
    def description(self) -> _StrOrPromise:
        return _("aaaa")
