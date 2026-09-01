from __future__ import annotations

from typing import assert_type

from django.contrib.postgres import fields as pg_fields
from django.db import models
from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange


class Booking(models.Model):
    time_range = pg_fields.DateTimeRangeField(null=False)
    null_time_range = pg_fields.DateTimeRangeField(null=True)
    int_range = pg_fields.IntegerRangeField()
    null_decimal_range = pg_fields.DecimalRangeField(null=True, default_bounds="[]")
    null_date_range = pg_fields.DateRangeField(null=True)


def range_fields_read_null_true_as_optional() -> None:
    booking = Booking()
    assert_type(booking.time_range, DateTimeTZRange)
    assert_type(booking.null_time_range, DateTimeTZRange | None)
    assert_type(booking.int_range, NumericRange)
    assert_type(booking.null_decimal_range, NumericRange | None)
    assert_type(booking.null_date_range, DateRange | None)
