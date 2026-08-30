# PR #3317 — Drawbacks of the PEP 696 `_NT` approach

Summary of the current state and the issues it causes for existing user code.

## Root cause

The PR adds a third TypeVar `_NT` (nullability flag) to `Field` with PEP 696
defaults: `Generic[_ST, _GT, _NT]` where `_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])`.
Outside the mypy plugin, those defaults short-circuit type inference for
unparametrized subclasses.

## Breaking changes for existing user code

### 1. Bare custom field subclasses lose `null=True` inference (without the plugin)

```python
class HTMLField(models.TextField): ...

body = HTMLField(null=True)
# -> TextField[str, str, Literal[False]]
# error: Argument "null" to "HTMLField" has incompatible type "Literal[True]";
#        expected "Literal[False]"
```

The mypy plugin papers over this by reparametrizing `HTMLField` to remain
generic in `_ST_Text`, `_GT_Text`, `_NT`. Every other checker
(pyright / pyrefly / ty / zuban) requires the user to rewrite their custom
fields with the explicit typevars:

```python
_ST_Text = TypeVar("_ST_Text", contravariant=True, default=str | int | Combinable)
_GT_Text = TypeVar("_GT_Text", covariant=True, default=str)
_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])

class HtmlField(models.TextField[_ST_Text, _GT_Text, _NT]):
    pass
```

Documented in the README, but still a migration burden for every custom field
in every downstream project.

### 2. `Field[A, B]` annotations change meaning silently

`Field[A, B]` no longer means "Field with set type `A`, get type `B`"; it
now implicitly means `Field[A, B, Literal[False]]` (non-null).

- `field: Field[A, B] = CustomField()` — still works.
- `field: Field[A, B] = CustomField(null=True)` — now errors.

Recommended fix is to delete the `: Field[A, B]` annotation entirely, but any
existing codebase using it as a workaround over nullable fields breaks.

### 3. `Field[_ST, _GT, bool]` is silently accepted but breaks narrowing

Nothing at the stub level prevents users from writing `bool` in the `_NT`
slot. When they do, `Literal[True]` / `Literal[False]` collapse to `bool` and
the `__get__` overload that narrows to `_GT | None` no longer fires.

### 5. Plugin / non-plugin divergence widens

- mypy + plugin: works via reparametrization.
- pyright / pyrefly / ty / zuban: require manual typevar boilerplate on every
  custom field.

The "works for mypy users" path masks how much typing work non-mypy users
inherit — the exact opposite of the PR's "stubs visible to all type
checkers" goal.

### 6. Ordering lock-in

`_NT` must come last (PEP 696 forbids a no-default TypeVar after defaulted
ones), so reordering to `Generic[_NT, _ST, _GT]` is rejected precisely
*because* it would change `Field[X, Y]`'s meaning. But the current solution
still changes it (to imply non-null) — just less visibly.

## Alternatives considered and rejected

### Drop `default=Literal[False]` from `_NT`

Violates PEP 696 ordering, so it would require either:

- Reordering to `Generic[_NT, _ST, _GT]` — changes the meaning of existing
  `Field[X, Y]` annotations completely.
- Dropping the `_ST` / `_GT` defaults and inlining them — makes custom field
  subclassing anything other than `Field` very difficult; users would have to
  redeclare the whole `__get__` / `__set__` machinery. Also requires
  `null: _NT = False`, which only works with pyright and pyrefly. mypy and ty
  do not support TypeVar default values:
    - mypy: <https://github.com/python/mypy/issues/3737> — works with a
      `type: ignore`.
    - ty: <https://github.com/astral-sh/ty/issues/592> — even with an ignore,
      inference breaks and produces `Unknown`.

### `_NT = TypeVar("_NT", Literal[False], Literal[True], default=Any)`

Breaks narrowing to `_GT` or `_GT | None` based on `null=...` because
`Literal[False]` / `Literal[True]` widen to `bool`. Blocker.

## Net trade-off

Stubs become correct without the plugin for null-tracking, at the cost of:

- (a) annotation churn on all custom field subclasses,
- (b) silent semantic shift of `Field[X, Y]` to non-null,
- (c) a remaining mypy-plugin dependency to make bare custom-field
  instantiation ergonomic — which is the opposite of the PR's
  "remove plugin code" goal.

## Followups tracked on the PR

- Upstream pyrefly issue for the `__get__` overload false positive.
- Upstream ty issue for the `# TODO: ty should reject that too` case.
- Support `ForeignKey` / `OneToOne` / `ManyToMany` with minimal plugin work.
