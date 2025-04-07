from collections.abc import Callable, Iterable
from typing import Any, TypeAlias, TypeVar

from django.http.response import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin
from django.views.generic.base import View

_ViewType = TypeVar("_ViewType", bound=View | Callable[..., Any])  # Any callable
_CallableType = TypeVar("_CallableType", bound=Callable[..., Any])
_DECORATOR: TypeAlias = Callable[..., Callable[..., HttpResponseBase] | Callable[..., Callable[..., HttpResponseBase]]]

classonlymethod = classmethod

def method_decorator(
    decorator: _DECORATOR | Iterable[_DECORATOR], name: str = ""
) -> Callable[[_ViewType], _ViewType]: ...
def decorator_from_middleware_with_args(middleware_class: type) -> _DECORATOR: ...
def decorator_from_middleware(middleware_class: type) -> _DECORATOR: ...
def make_middleware_decorator(middleware_class: type[MiddlewareMixin]) -> _DECORATOR: ...
def sync_and_async_middleware(func: _CallableType) -> _CallableType: ...
def sync_only_middleware(func: _CallableType) -> _CallableType: ...
def async_only_middleware(func: _CallableType) -> _CallableType: ...
