from typing import Any, Literal

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.expressions import Combinable
from django.http.request import HttpRequest
from typing_extensions import override

SITE_CACHE: Any

class SiteManager(models.Manager[Site]):
    def get_current(self, request: HttpRequest | None = ...) -> Site: ...
    def clear_cache(self) -> None: ...
    def get_by_natural_key(self, domain: str) -> Site: ...

# Declaring `objects` on the metaclass keeps it a fallback, so a subclass can replace it.
class _SiteModelBase(ModelBase):
    @override
    def __getattr__(cls: type[Site], name: Literal["objects"]) -> SiteManager: ...  # type: ignore[misc, override]

class Site(models.Model, metaclass=_SiteModelBase):
    domain: models.CharField[str | int | Combinable, str]
    name: models.CharField[str | int | Combinable, str]
    def natural_key(self) -> tuple[str]: ...

def clear_site_cache(sender: type[Site], **kwargs: Any) -> None: ...
