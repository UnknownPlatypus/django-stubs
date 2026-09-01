from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse, reverse_lazy

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

reversed_url = reverse("url")
lazy_url = reverse_lazy("namespace:url")


# pyrefly doesn't apply the descriptor protocol to the union-typed
# `AbstractBaseUser.is_active: bool | BooleanField[...]`, so the lambda returns
# `BooleanField | bool` for it. No upstream issue yet.
@user_passes_test(lambda user: user.is_active, login_url=reversed_url)  # pyrefly: ignore[bad-argument-type]
def my_view1(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


@user_passes_test(lambda user: user.is_active, login_url=lazy_url)  # pyrefly: ignore[bad-argument-type]
def my_view2(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError
