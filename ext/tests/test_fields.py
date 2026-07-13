from __future__ import annotations

from django_stubs_ext import FieldInitKwargs


def test_field_init_kwargs_is_closed() -> None:
    # `closed=True` is load-bearing: it is what makes ty reject unknown keys
    # passed through `**kwargs: Unpack[FieldInitKwargs[...]]`.
    assert FieldInitKwargs.__closed__ is True  # type: ignore[attr-defined]


def test_field_init_kwargs_is_generic() -> None:
    # Parametrization must work at runtime for user code importing it.
    kwargs: FieldInitKwargs[int] = {"primary_key": True, "db_default": 3}
    assert kwargs == {"primary_key": True, "db_default": 3}
