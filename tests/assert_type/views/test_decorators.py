from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, assert_type

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page, never_cache
from django.views.decorators.clickjacking import xframe_options_deny, xframe_options_exempt, xframe_options_sameorigin
from django.views.decorators.common import no_append_slash
from django.views.decorators.csp import csp_override, csp_report_only_override
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie, requires_csrf_token
from django.views.decorators.gzip import gzip_page
from django.views.decorators.http import (
    condition,
    conditional_page,
    etag,
    last_modified,
    require_GET,
    require_http_methods,
    require_POST,
    require_safe,
)
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from typing_extensions import override

if TYPE_CHECKING:
    from datetime import datetime

    from django.contrib.auth.models import User
    from django.http.response import HttpResponseBase


@csp_override(
    {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "report-uri": "/path/to/reports-endpoint/",
    }
)
def my_view(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


@csp_report_only_override(
    {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "report-uri": "/path/to/reports-endpoint/",
    }
)
def my_view2(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(my_view(HttpRequest()), HttpResponse)
assert_type(my_view2(HttpRequest()), HttpResponse)


def compute_etag(request: HttpRequest, pk: int) -> str | None:
    return None


def compute_last_modified(request: HttpRequest, pk: int) -> datetime | None:
    return None


# Every view decorator keeps the exact signature of a plain view.
@cache_page(60, key_prefix="p")
@cache_control(max_age=60)
@never_cache
@xframe_options_deny
@xframe_options_sameorigin
@xframe_options_exempt
@no_append_slash
@csrf_protect
@requires_csrf_token
@ensure_csrf_cookie
@csrf_exempt
@gzip_page
@conditional_page
@require_http_methods(["GET"])
@require_GET
@require_POST
@require_safe
@condition(etag_func=compute_etag)
@etag(compute_etag)
@last_modified(compute_last_modified)
@vary_on_headers("Accept")
@vary_on_cookie
def all_decorators(request: HttpRequest, pk: int, *, slug: str = "") -> HttpResponse:
    raise NotImplementedError


assert_type(all_decorators(HttpRequest(), 1, slug="s"), HttpResponse)
assert_type(all_decorators(request=HttpRequest(), pk=1), HttpResponse)


@csrf_exempt
async def async_view(request: HttpRequest, pk: int) -> JsonResponse:
    raise NotImplementedError


@cache_page(60)
async def async_factory_view(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


async def call_async() -> None:
    assert_type(await async_view(HttpRequest(), pk=1), JsonResponse)
    assert_type(await async_factory_view(HttpRequest()), HttpResponse)
    assert_type(await async_authenticated_view(AuthenticatedHttpRequest()), JsonResponse)


@csrf_exempt
def positional_only_view(request: HttpRequest, /, pk: int) -> StreamingHttpResponse:
    raise NotImplementedError


@csrf_exempt
def union_response_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    raise NotImplementedError


@csrf_exempt
def untyped_view(*args: Any, **kwargs: Any) -> Any:
    raise NotImplementedError


assert_type(positional_only_view(HttpRequest(), 1), StreamingHttpResponse)
assert_type(union_response_view(HttpRequest()), HttpResponse | HttpResponseRedirect)
assert_type(untyped_view(HttpRequest()), Any)

# `View.as_view()`, `functools.partial` and already decorated views are views too.
csrf_exempt(View.as_view())
csrf_exempt(partial(all_decorators, pk=1))
path("inline/", cache_page(60)(positional_only_view))


# `request` isn't checked: wrappers like DRF's `Request` don't subclass `HttpRequest`.
class WrappedRequest:
    pass


@csrf_exempt
def wrapped_request_view(request: WrappedRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(wrapped_request_view(WrappedRequest()), HttpResponse)


@csrf_exempt
@login_required
def stacked_view(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(stacked_view(HttpRequest()), HttpResponse)


# Applied directly on a method, `self` comes before `request`.
class DirectlyDecoratedView(View):
    @csrf_exempt
    @override
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        raise NotImplementedError

    @require_POST
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        raise NotImplementedError

    @never_cache
    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        raise NotImplementedError


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(cache_page(60), name="get")
class MethodDecoratedView(View):
    pass


assert_type(DirectlyDecoratedView().post(HttpRequest(), 1), JsonResponse)


# The README's recipe narrows `request` to a subclass; the decorated view stays callable the same way.
class AuthenticatedHttpRequest(HttpRequest):
    user: User  # pyright: ignore[reportIncompatibleVariableOverride]  # pyrefly: ignore[bad-override]  # ty: ignore[invalid-mutable-override]


@csrf_exempt
@login_required
def authenticated_view(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    raise NotImplementedError


@cache_page(60)
async def async_authenticated_view(request: AuthenticatedHttpRequest) -> JsonResponse:
    raise NotImplementedError


assert_type(authenticated_view(AuthenticatedHttpRequest(), 1), HttpResponse)
assert_type(authenticated_view(request=AuthenticatedHttpRequest(), pk=1), HttpResponse)
authenticated_view(HttpRequest(), 1)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-argument-type]


# Not views: the decorators reject them.
@csrf_exempt  # type: ignore[type-var]  # pyright: ignore[reportArgumentType, reportUntypedFunctionDecorator]  # pyrefly: ignore[bad-specialization]  # ty: ignore[invalid-argument-type]
def not_a_response(request: HttpRequest) -> str:
    raise NotImplementedError


@csrf_exempt  # type: ignore[type-var]  # pyright: ignore[reportArgumentType, reportUntypedFunctionDecorator]  # pyrefly: ignore[bad-specialization]  # ty: ignore[invalid-argument-type]
def no_request(*, pk: int) -> HttpResponse:
    raise NotImplementedError
