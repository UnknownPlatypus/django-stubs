# Field `null=True` Typing — Findings

Summary of investigation comparing the PEP 696 `_NT` TypeVar approach used on this branch (`pep696-field-typing-skip-null-any`) with the `__new__`-overload approach from [django-types](https://github.com/sbdchd/django-types/blob/main/django-stubs/db/models/fields/__init__.pyi), referenced in [PR #3317](https://github.com/typeddjango/django-stubs/pull/3317).

## The problem

A Django field declared with `null=True` should:
- have `__get__` return `T | None` on model-instance access
- have `__set__` accept `None`

…and conversely `null=False` (or unspecified) should have `__get__` return `T` and `__set__` reject `None`. The challenge is making both branches type-check consistently across mypy, pyright, ty, and pyrefly without plugin help, while keeping bare `Field[A, B]` annotations from leaking unwanted nullability assumptions.

## Approaches investigated

### PEP 696 `_NT` TypeVar (current branch)

```python
_NT = TypeVar("_NT", Literal[True], Literal[False], default=...)

class Field(Generic[_ST, _GT, _NT]):
    def __init__(self, *, null: _NT = False, ...) -> None: ...

    @overload
    def __set__(self: Field[Any, Any, Literal[False]], i: Any, v: _ST | Combinable) -> None: ...
    @overload
    def __set__(self: Field[Any, Any, Literal[True]], i: Any, v: _ST | Combinable | None) -> None: ...
    @overload
    def __set__(self, i: Any, v: _ST | Combinable) -> None: ...
```

**Pros**
- Subclasses inherit nullability propagation for free (one typevar passed through).
- No constructor-kwargs duplication.
- Composes with future flag-driven typevars (e.g. `_PT` for `primary_key`).
- Plugin can reparametrize `_NT` through `ForeignKey`/`OneToOneField`.

**Cons**
- `default=Literal[False]` makes bare `Field[A, B]` annotations silently bind `_NT=Literal[False]`, leaking nullability semantics into existing user code.
- `default=Any` (current workaround, with `# type: ignore[misc]`) avoids the bare-annotation leak but the third fallback `__set__` overload swallows the implicit-`null=False` set check — `book.title = None` is silently accepted.
- pyright additionally flags `default=Any` as `reportGeneralTypeIssues` ("TypeVar default type must be one of the constrained types").

### `__new__` overloads on subclasses (django-types)

```python
class IntegerField(Field[_I | Combinable, _I], Generic[_I]):
    @overload
    def __new__(cls, *, null: Literal[False] = False, ...) -> IntegerField[int]: ...
    @overload
    def __new__(cls, *, null: Literal[True], ...) -> IntegerField[int | None]: ...
```

**Pros**
- Catches `book.title = None` even with implicit `null=False`, because `_GT` resolves directly at construction.
- Consistent across all four checkers without plugin help.
- `Field[A, B]` stays nullability-agnostic.

**Cons**
- Every concrete subclass redeclares its full kwargs list × 2 overloads.
- User subclasses without their own `__new__` overloads lose null-typing.
- Adding a second flag (e.g. `primary_key`) explodes overloads multiplicatively unless the setter type is moved to a separate generic parameter.

## Sub-options explored for the `_NT` approach

| Option | Strategy | Implicit `null=False` set check | Bare `Field[A,B]` safe | Works on all 4 checkers |
|---|---|---|---|---|
| Current | `default=Any`, 3-overload `__set__` | ❌ silently accepted | ✓ | ✓ (pyright flag aside) |
| **A** | drop the fallback `__set__` overload | ❌ mypy/ty/pyrefly pick the nullable overload | ✓ | ❌ |
| **B** | overload `__init__` with `self: Field[..., Literal[X]]` self-types | ✓ on mypy/ty/pyrefly | ✓ | ❌ (pyright `reportInvalidTypeVarUse`) |
| **C** | `__new__` overloads on each subclass; keep `_NT` typevar on `Field` | ✓ | ✓ | ✓ |

### Option C — recommended

`Field` keeps the `_NT` typevar (with `default=Any`), but each concrete subclass adds two `__new__` overloads that bind `_NT` definitively at construction time:

```python
class CharField(Field[_ST_Char, _GT_Char, _NT]):
    @overload
    def __new__(cls, *, null: Literal[False] = False, ...) -> CharField[_ST_Char, _GT_Char, Literal[False]]: ...
    @overload
    def __new__(cls, *, null: Literal[True], ...) -> CharField[_ST_Char, _GT_Char, Literal[True]]: ...
```

Verified:
- All 5 read-side reveals match (`str`, `int`, `str`, `str | None`, `int | None`) on every checker.
- All 3 `__set__` rejections fire on every checker, including implicit `null=False`.
- User subclasses of `CharField` (with no `__new__` of their own) inherit the overload behavior — `class MyCustomCharField(CharField[...]): pass` still rejects `instance.field = None` for the non-null case.
- `null=bool(...)` either errors (mypy/ty/pyrefly) or resolves to a union of both overload returns (pyright) — no false positive on the read side either way.
- `Field[str, str]` bare annotation resolves to `Field[str, str, Any]` everywhere.
- Pyright still emits one diagnostic at the `_NT` declaration for `default=Any` violating PEP 696's constrained-default rule. Suppressible with `# pyright: ignore[reportGeneralTypeIssues]`.

## Future: `primary_key=True` accepting `None` on the setter

When `primary_key=True`, `instance.pk = None` should be allowed (clone-and-save idiom). The getter type should stay non-`None`.

This is where the `__new__`-only approach (django-types-style) breaks down: with no `_NT`-equivalent typevar to encode the relaxation, each subclass needs `2 × 2 = 4` overloads, and the setter/getter divergence forces either an extra generic param or a separate class.

Option C scales naturally — add a second typevar:

```python
_PT = TypeVar("_PT", Literal[True], Literal[False], default=Any)

class Field(Generic[_ST, _GT, _NT, _PT]):
    @overload
    def __set__(self: Field[Any, Any, Literal[True], Any], i, v: _ST | Combinable | None) -> None: ...
    @overload
    def __set__(self: Field[Any, Any, Any, Literal[True]], i, v: _ST | Combinable | None) -> None: ...
    @overload
    def __set__(self: Field[Any, Any, Literal[False], Literal[False]], i, v: _ST | Combinable) -> None: ...
    # __get__ stays unchanged — pk doesn't affect read type
```

Each leaf subclass's `__new__` grows from 2 overloads to 4 to cover the cross-product. The hierarchy above the leaves (`SmallIntegerField → IntegerField`) doesn't need to change.

## Reproductions

The three sub-option snippets are checked in at the repo root for verification:

- `repro_null_a.py` — Option A (drop fallback overload)
- `repro_null_b.py` — Option B (overload `__init__`)
- `repro_null_c.py` — Option C (`__new__` overloads on subclasses) — **recommended**

Run with:

```bash
uv run mypy --no-incremental repro_null_c.py
uv run pyright repro_null_c.py
uv run ty check repro_null_c.py
uv run pyrefly check repro_null_c.py
```
