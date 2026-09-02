"""Django's own models expose `objects` the same way a plain `models.Model` does.

The specialized manager resolves on the class, is unreachable from an instance, and a
subclass can replace it with its own, the way Django allows at runtime.
"""

from __future__ import annotations

from typing import assert_type

from django.contrib.admin.models import LogEntry, LogEntryManager
from django.contrib.auth.models import Group, GroupManager, Permission, PermissionManager, User, UserManager
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.contrib.sessions.base_session import AbstractBaseSession, BaseSessionManager
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site, SiteManager


def specialized_manager_access_on_class_is_allowed() -> None:
    assert_type(LogEntry.objects, LogEntryManager)
    assert_type(Permission.objects, PermissionManager)
    assert_type(Group.objects, GroupManager)
    assert_type(ContentType.objects, ContentTypeManager)
    assert_type(Site.objects, SiteManager)
    # Declared on an abstract base, so the manager binds to the concrete model
    assert_type(User.objects, UserManager[User])
    assert_type(Session.objects, BaseSessionManager[Session])


def specialized_manager_access_on_instance_is_banned() -> None:
    # The fallback lives on the metaclass, so instances can't reach it at all
    Site().objects  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # pyrefly: ignore[missing-attribute]  # ty: ignore[unresolved-attribute]
    User().objects  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # pyrefly: ignore[missing-attribute]  # ty: ignore[unresolved-attribute]


def unknown_attribute_is_still_an_error() -> None:
    # A specialized `objects` must not turn the metaclass lookup into a catch-all
    Site.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]
    User.not_defined  # type: ignore[attr-defined]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-attribute-access]


# ---------------------------------------------------------------------------
# Overriding the manager inherited from a concrete builtin model
# ---------------------------------------------------------------------------


class MySiteManager(SiteManager):
    pass


class MySite(Site):
    objects = MySiteManager()


def concrete_builtin_manager_can_be_overridden() -> None:
    assert_type(MySite.objects, MySiteManager)


# ---------------------------------------------------------------------------
# Overriding the manager inherited from an abstract builtin model
# Regression test for https://github.com/typeddjango/django-stubs/issues/174
# ---------------------------------------------------------------------------


class DepositClientManager(UserManager["DepositClient"]):
    pass


class DepositClient(User):
    objects = DepositClientManager()


def abstract_builtin_manager_can_be_overridden() -> None:
    assert_type(DepositClient.objects, DepositClientManager)


class CustomSessionManager(BaseSessionManager["CustomSession"]):
    pass


class CustomSession(AbstractBaseSession):
    objects = CustomSessionManager()


def abstract_base_session_manager_can_be_overridden() -> None:
    assert_type(CustomSession.objects, CustomSessionManager)
