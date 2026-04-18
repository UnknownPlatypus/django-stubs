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

_ST_Point = TypeVar("_ST_Point", default=Point | Combinable)
_GT_Point = TypeVar("_GT_Point", default=Point)
_ST_LineString = TypeVar("_ST_LineString", default=LineString | Combinable)
_GT_LineString = TypeVar("_GT_LineString", default=LineString)
_ST_Polygon = TypeVar("_ST_Polygon", default=Polygon | Combinable)
_GT_Polygon = TypeVar("_GT_Polygon", default=Polygon)
_ST_MultiPoint = TypeVar("_ST_MultiPoint", default=MultiPoint | Combinable)
_GT_MultiPoint = TypeVar("_GT_MultiPoint", default=MultiPoint)
_ST_MultiLineString = TypeVar("_ST_MultiLineString", default=MultiLineString | Combinable)
_GT_MultiLineString = TypeVar("_GT_MultiLineString", default=MultiLineString)
_ST_MultiPolygon = TypeVar("_ST_MultiPolygon", default=MultiPolygon | Combinable)
_GT_MultiPolygon = TypeVar("_GT_MultiPolygon", default=MultiPolygon)
_ST_GeometryCollection = TypeVar("_ST_GeometryCollection", default=GeometryCollection | Combinable)
_GT_GeometryCollection = TypeVar("_GT_GeometryCollection", default=GeometryCollection)

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

class PointField(GeometryField[_ST_Point, _GT_Point]):
    _pyi_lookup_exact_type: Point

    geom_class: type[Point]
    form_class: type[forms.PointField]

class LineStringField(GeometryField[_ST_LineString, _GT_LineString]):
    _pyi_lookup_exact_type: LineString

    geom_class: type[LineString]
    form_class: type[forms.LineStringField]

class PolygonField(GeometryField[_ST_Polygon, _GT_Polygon]):
    _pyi_lookup_exact_type: Polygon

    geom_class: type[Polygon]
    form_class: type[forms.PolygonField]

class MultiPointField(GeometryField[_ST_MultiPoint, _GT_MultiPoint]):
    _pyi_lookup_exact_type: MultiPoint

    geom_class: type[MultiPoint]
    form_class: type[forms.MultiPointField]

class MultiLineStringField(GeometryField[_ST_MultiLineString, _GT_MultiLineString]):
    _pyi_lookup_exact_type: MultiLineString

    geom_class: type[MultiLineString]
    form_class: type[forms.MultiLineStringField]

class MultiPolygonField(GeometryField[_ST_MultiPolygon, _GT_MultiPolygon]):
    _pyi_lookup_exact_type: MultiPolygon

    geom_class: type[MultiPolygon]
    form_class: type[forms.MultiPolygonField]

class GeometryCollectionField(GeometryField[_ST_GeometryCollection, _GT_GeometryCollection]):
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
