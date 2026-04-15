from collections.abc import Iterable
from typing import Any, NamedTuple

from django.contrib.gis import forms
from django.contrib.gis.geos import (
    GeometryCollection,
    GEOSGeometry,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from django.core.validators import _ValidatorCallable
from django.db.models import Model
from django.db.models.expressions import Combinable, Expression
from django.db.models.fields import NOT_PROVIDED, Field, _ErrorMessagesMapping
from django.utils.choices import _Choices
from django.utils.functional import _StrOrPromise
from typing_extensions import TypeVar, override

# __set__ value type
_ST = TypeVar("_ST")
# __get__ return type
_GT = TypeVar("_GT")

_ST_POINT = TypeVar("_ST_POINT", default=Point | Combinable)
_GT_POINT = TypeVar("_GT_POINT", default=Point)
_ST_LINESTRING = TypeVar("_ST_LINESTRING", default=LineString | Combinable)
_GT_LINESTRING = TypeVar("_GT_LINESTRING", default=LineString)
_ST_POLYGON = TypeVar("_ST_POLYGON", default=Polygon | Combinable)
_GT_POLYGON = TypeVar("_GT_POLYGON", default=Polygon)
_ST_MULTIPOINT = TypeVar("_ST_MULTIPOINT", default=MultiPoint | Combinable)
_GT_MULTIPOINT = TypeVar("_GT_MULTIPOINT", default=MultiPoint)
_ST_MULTILINESTRING = TypeVar("_ST_MULTILINESTRING", default=MultiLineString | Combinable)
_GT_MULTILINESTRING = TypeVar("_GT_MULTILINESTRING", default=MultiLineString)
_ST_MULTIPOLYGON = TypeVar("_ST_MULTIPOLYGON", default=MultiPolygon | Combinable)
_GT_MULTIPOLYGON = TypeVar("_GT_MULTIPOLYGON", default=MultiPolygon)
_ST_GEOMCOLLECTION = TypeVar("_ST_GEOMCOLLECTION", default=GeometryCollection | Combinable)
_GT_GEOMCOLLECTION = TypeVar("_GT_GEOMCOLLECTION", default=GeometryCollection)

class SRIDCacheEntry(NamedTuple):
    units: Any
    units_name: str
    spheroid: str
    geodetic: bool

def get_srid_info(srid: int, connection: Any) -> SRIDCacheEntry: ...

class BaseSpatialField(Field[_ST, _GT]):
    form_class: type[forms.GeometryField]
    geom_type: str
    geom_class: type[GEOSGeometry] | None
    geography: bool
    spatial_index: bool
    srid: int
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        srid: int = 4326,
        spatial_index: bool = True,
        *,
        name: str | None = ...,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _Choices | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[_ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def db_type(self, connection: Any) -> Any: ...
    def spheroid(self, connection: Any) -> Any: ...
    def units(self, connection: Any) -> Any: ...
    def units_name(self, connection: Any) -> Any: ...
    def geodetic(self, connection: Any) -> Any: ...
    def get_placeholder(self, value: Any, compiler: Any, connection: Any) -> Any: ...
    def get_srid(self, obj: Any) -> Any: ...
    @override
    def get_db_prep_value(self, value: Any, connection: Any, *args: Any, **kwargs: Any) -> Any: ...
    def get_raster_prep_value(self, value: Any, is_candidate: Any) -> Any: ...
    @override
    def get_prep_value(self, value: Any) -> Any: ...

class GeometryField(BaseSpatialField[_ST, _GT]):
    dim: int
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        dim: int = 2,
        geography: bool = False,
        *,
        extent: tuple[float, float, float, float] = ...,
        tolerance: float = 0.05,
        srid: int = 4326,
        spatial_index: bool = True,
        name: str | None = ...,
        primary_key: bool = ...,
        max_length: int | None = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        db_default: type[NOT_PROVIDED] | Expression | _ST = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        unique_for_date: str | None = ...,
        unique_for_month: str | None = ...,
        unique_for_year: str | None = ...,
        choices: _Choices | None = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_comment: str | None = ...,
        db_tablespace: str | None = ...,
        validators: Iterable[_ValidatorCallable] = ...,
        error_messages: _ErrorMessagesMapping | None = ...,
    ) -> None: ...
    @override
    def contribute_to_class(self, cls: type[Model], name: str, **kwargs: Any) -> None: ...  # type: ignore[override]
    @override
    def formfield(  # type: ignore[override]
        self,
        *,
        form_class: type[forms.GeometryField] | None = ...,
        geom_type: str = ...,
        srid: Any = ...,
        **kwargs: Any,
    ) -> forms.GeometryField: ...

class PointField(GeometryField[_ST_POINT, _GT_POINT]):
    _pyi_lookup_exact_type: Point

    geom_class: type[Point]
    form_class: type[forms.PointField]

class LineStringField(GeometryField[_ST_LINESTRING, _GT_LINESTRING]):
    _pyi_lookup_exact_type: LineString

    geom_class: type[LineString]
    form_class: type[forms.LineStringField]

class PolygonField(GeometryField[_ST_POLYGON, _GT_POLYGON]):
    _pyi_lookup_exact_type: Polygon

    geom_class: type[Polygon]
    form_class: type[forms.PolygonField]

class MultiPointField(GeometryField[_ST_MULTIPOINT, _GT_MULTIPOINT]):
    _pyi_lookup_exact_type: MultiPoint

    geom_class: type[MultiPoint]
    form_class: type[forms.MultiPointField]

class MultiLineStringField(GeometryField[_ST_MULTILINESTRING, _GT_MULTILINESTRING]):
    _pyi_lookup_exact_type: MultiLineString

    geom_class: type[MultiLineString]
    form_class: type[forms.MultiLineStringField]

class MultiPolygonField(GeometryField[_ST_MULTIPOLYGON, _GT_MULTIPOLYGON]):
    _pyi_lookup_exact_type: MultiPolygon

    geom_class: type[MultiPolygon]
    form_class: type[forms.MultiPolygonField]

class GeometryCollectionField(GeometryField[_ST_GEOMCOLLECTION, _GT_GEOMCOLLECTION]):
    _pyi_lookup_exact_type: GeometryCollection

    geom_class: type[GeometryCollection]
    form_class: type[forms.GeometryCollectionField]

class ExtentField(Field[Any, Any]):
    @override
    def get_internal_type(self) -> str: ...

class RasterField(BaseSpatialField):
    @override
    def db_type(self, connection: Any) -> Any: ...
    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Any: ...
    @override
    def contribute_to_class(self, cls: type[Model], name: str, **kwargs: Any) -> None: ...  # type: ignore[override]
    @override
    def get_transform(self, name: Any) -> Any: ...
