from __future__ import annotations

from typing import TYPE_CHECKING, Any, assert_type

from django.db import connection, connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper

if TYPE_CHECKING:
    from collections.abc import Callable

with connection.cursor() as cursor:
    assert_type(cursor, CursorWrapper)
    cursor.execute("SELECT %s", [123])

# psycopg2 composable SQL
from psycopg2.sql import SQL, Identifier

with connection.cursor() as cursor:
    cursor.execute(SQL("INSERT INTO {} VALUES (%s)").format(Identifier("my_table")), [123])

assert_type(connections["test"], BaseDatabaseWrapper)
for conn in connections.all():
    with conn.cursor() as cursor:
        assert_type(cursor, CursorWrapper)


def blocker(
    execute: Callable[[str, Any, bool, dict[str, Any]], Any], sql: str, params: Any, many: bool, context: dict[str, Any]
) -> Any:
    return execute(sql, params, many, context)


with connection.execute_wrapper(blocker) as entered:
    assert_type(entered, None)
with connection.constraint_checks_disabled() as disabled:
    assert_type(disabled, None)
