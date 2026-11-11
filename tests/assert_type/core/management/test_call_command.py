from __future__ import annotations

from django.core.management import call_command


# Most commands return None, a few (e.g. sqlmigrate) return their output
def migrate_returns_none() -> None:
    if call_command("migrate") is None:
        return


def sqlmigrate_returns_str() -> None:
    call_command("sqlmigrate", "app", "0001").splitlines()
