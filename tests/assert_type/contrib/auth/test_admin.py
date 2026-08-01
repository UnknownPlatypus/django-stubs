from __future__ import annotations

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# `UserAdmin` always defines `fieldsets`, so extending it doesn't need a `None` check.
class ExtendedUserAdmin(UserAdmin[User]):
    fieldsets = [*UserAdmin.fieldsets, ("Extra", {"fields": ["nickname"]})]
