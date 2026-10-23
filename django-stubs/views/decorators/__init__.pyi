from collections.abc import Awaitable, Callable
from typing import Any, Concatenate

from django.http.response import HttpResponseBase
from typing_extensions import TypeVar

# A view: `request` first (or `self` when decorating a method) and a response back.
# `request` is `Any` rather than `HttpRequest` so views narrowing it to a subclass
# (the README's `AuthenticatedHttpRequest` recipe) still match.
_ViewFuncT = TypeVar(  # noqa: PYI018
    "_ViewFuncT", bound=Callable[Concatenate[Any, ...], HttpResponseBase | Awaitable[HttpResponseBase]]
)
