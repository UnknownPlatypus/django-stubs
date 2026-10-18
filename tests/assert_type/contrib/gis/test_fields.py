from __future__ import annotations

from typing import assert_type

from django.contrib.gis.db.models import fields
from django.contrib.gis.geos import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from django.db import models


class Geo(models.Model):
    point = fields.PointField()
    null_point = fields.PointField(null=True)
    line_string = fields.LineStringField(null=True)
    polygon = fields.PolygonField(null=True)
    multi_point = fields.MultiPointField(null=True)
    multi_line_string = fields.MultiLineStringField(null=True)
    multi_polygon = fields.MultiPolygonField(null=True)
    geometry_collection = fields.GeometryCollectionField(null=True)


def nullable_geometry_fields_read_optional() -> None:
    geo = Geo()
    assert_type(geo.point, Point)
    assert_type(geo.null_point, Point | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.line_string, LineString | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.polygon, Polygon | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.multi_point, MultiPoint | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.multi_line_string, MultiLineString | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.multi_polygon, MultiPolygon | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(geo.geometry_collection, GeometryCollection | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    geo.null_point = None  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-assignment]
    geo.point = None  # type: ignore[assignment]  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-assignment]
