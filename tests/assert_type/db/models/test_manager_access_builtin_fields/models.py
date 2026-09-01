"""Managers are only accessible on the model class, never on an instance."""

from __future__ import annotations

from typing import assert_type

from django.contrib.auth.models import User, UserManager
from django.contrib.sites.models import Site, SiteManager


class MySiteManager(SiteManager):
    pass


class MySite(Site):
    objects = MySiteManager()


def can_override_site() -> None:
    assert_type(MySite.objects, MySiteManager)


## Regression test for https://github.com/typeddjango/django-stubs/issues/174
class MyUserManager(UserManager["DepositClient"]):
    pass


class DepositClient(User):
    objects = MyUserManager()


def can_override_user() -> None:
    assert_type(DepositClient.objects, MyUserManager)


def unknown_attribute_is_still_an_error() -> None:
    # `Literal["objects"]` must not turn the stub metaclasses `__getattr__` into a catch-all
    Site.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]
    User.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]
