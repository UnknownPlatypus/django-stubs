from __future__ import annotations

from django_stubs_ext import FieldInitKwargs


def test_field_init_kwargs_is_closed() -> None:
    # `closed=True` is load-bearing: it is what makes ty reject unknown keys
    # passed through `**kwargs: Unpack[FieldInitKwargs[...]]`.
    assert getattr(FieldInitKwargs, "__closed__", None) is True
