"""Overriding `objects` when subclassing a model that declares a custom manager."""

from __future__ import annotations

from typing import assert_type

from django.db import models
from typing_extensions import TypeVar

_UserT = TypeVar("_UserT", bound="MyBaseUser", default="MyBaseUser", covariant=True)


class MyBaseManager(models.Manager[_UserT]):
    pass


class MyBaseUser(models.Model):
    objects = MyBaseManager()


class MyManager(MyBaseManager["MyUser"]):
    pass


class MyUser(MyBaseUser):
    objects = MyManager()


def overriding_objects_with_a_compatible_manager_is_allowed() -> None:
    assert_type(MyBaseUser.objects, MyBaseManager[MyBaseUser])
    assert_type(MyBaseUser.objects.get(), MyBaseUser)
    assert_type(MyUser.objects, MyManager)
    assert_type(MyUser.objects.get(), MyUser)


class UnrelatedManager(models.Manager["OtherUser"]):
    pass


class OtherUser(MyBaseUser):
    # An `objects` override must stay compatible with the manager inherited from the parent model.
    # Only mypy and pyrefly check the compatibility of this unannotated assignment.
    objects = UnrelatedManager()  # type: ignore[assignment]  # pyrefly: ignore[bad-override]
