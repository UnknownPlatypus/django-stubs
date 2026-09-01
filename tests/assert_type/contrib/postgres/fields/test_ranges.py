from __future__ import annotations

from typing import Any, assert_type

from django.contrib.postgres import fields as pg_fields
from django.db import models


class Booking(models.Model):
    time_range = pg_fields.DateTimeRangeField(null=False)
    null_time_range = pg_fields.DateTimeRangeField(null=True)


booking = Booking()
assert_type(booking.time_range, Any)  # pyrefly: ignore[assert-type] # ty: ignore[type-assertion-failure] # pyright: ignore[reportAssertTypeFailure]
assert_type(booking.null_time_range, Any)  # pyrefly: ignore[assert-type]# ty: ignore[type-assertion-failure]# pyright: ignore[reportAssertTypeFailure]
