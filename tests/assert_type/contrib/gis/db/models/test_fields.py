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
    assert_type(geo.null_point, Point | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.line_string, LineString | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.polygon, Polygon | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.multi_point, MultiPoint | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.multi_line_string, MultiLineString | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.multi_polygon, MultiPolygon | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    assert_type(geo.geometry_collection, GeometryCollection | None)  # ty: ignore[type-assertion-failure]  # https://github.com/astral-sh/ty/issues/3990
    geo.null_point = None  # ty: ignore[invalid-assignment]  # https://github.com/astral-sh/ty/issues/3990
    geo.point = None  # type: ignore[assignment]  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-assignment]
