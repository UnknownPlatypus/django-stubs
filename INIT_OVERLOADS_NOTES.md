# Branch notes — pep696-field-init-overloads

Implements the "concrete-self `__init__` overloads" design for field nullability
(validated on mypy/pyright/ty/pyrefly/zuban, see `NULL_TYPING_FINDINGS.md` + `fieldstubs.pyi`/`repro_null_n*.py`
on the `pep696-field-typing-skip-null-any` branch).
Forked from PR #3317's head; the `_NT` TypeVar is removed entirely.

## Background: PR #3317 and the `_NT` approach

PR #3317 ("Use PEP 696 for model fields") replaces the mypy-only `_pyi_private_set_type`/`_pyi_private_get_type`
attributes with PEP 696 TypeVar defaults, making field set/get types visible to every type checker.
It fixes #766, #1264, #1900, #2043, #2590, #2724 and improves #579.
Two encodings for `null=` emerged there:

1. **`__new__` overloads** (django-types' approach) — see "Why not `__new__`" below.
2. **`_NT` third TypeVar**: `Field[_ST, _GT, _NT]` with
   `_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])` and `__get__` overloads
   switching on `_NT` via `self: Field[Any, Any, Literal[True]]`. The PR shipped this; it works on all five
   checkers for direct fields (re-verified on ty 0.0.55, 2026-07).

Iterating on `_NT` surfaced structural problems (draft reply to @sobolevn, kept in `t.md`):

- `default=Literal[False]` silently re-types every existing annotation: `Field[A, B]` now means *non-null*,
  so pre-existing nullable annotations (`Field[str | None, str | None]`) mismatch loudly on all checkers.
- The `default=Any` variant un-poisons annotations but breaks bare construction: `CharField()` infers
  `_NT = Any` instead of `Literal[False]` on mypy/ty/pyrefly, because binding a TypeVar from the parameter
  default (`null: _NT = False`) is only implemented by pyright.
  Upstream: mypy#3737, ty#592, pyrefly#2711, conformance discussion python/typing#2213.
  Also, a constrained TypeVar with `default=Any` is spec-invalid (`# type: ignore[misc]` + pyright ignore),
  and ty 0.0.55 flags the `null: _NT = False` stub default as `invalid-parameter-default`.
- Bare custom subclasses (`class HTMLField(models.TextField): ...`) hard-error on `null=True` outside mypy
  ("expected `Literal[False]`"); mypy only survives because the plugin reparametrizes the subclass.
- Each future flag (`primary_key`, `default`, `db_default`) would need another TypeVar slot — combinatorial,
  and every slot change breaks annotations again ("the `_NT` thing is a big constraint").

The requirements distilled in `t.md` (any solution failing a hard requirement is not viable):

- **Hard**: `Field()` and `CustomField()` must infer non-null from the runtime/stub-declared default;
  the design must extend easily to `primary_key`/`default`/`db_default` narrowing.
- **Soft** (best effort): bare `Field` annotations stay `Field[Any, Any]`; `Field[A, B]` keeps its meaning;
  custom fields work out of the box with minimal changes.

This branch replaces `_NT` with per-field `__init__` overloads (design ⑥ of the investigation).

## Design (as implemented)

- `Field` is back to `Generic[_ST, _GT]` with PEP 696 defaults (`Any`), a single `__set__(value: _ST | Combinable)`,
  and 3 `__get__` overloads (class-access descriptor / model-instance `_GT` / non-model `Self`).
- Every concrete field class gets **2** `__init__` overloads
  (see `CharField` / `IntegerField` exemplars in `django-stubs/db/models/fields/__init__.pyi`):
  1. `self: C[<ST> | None, <GT> | None]`, keyword-only `null: Literal[True]`
     (folds `None` into both directions for `null=True`)
  2. fallback: the original positional signature with plain `bool` flags — handles `null=False`,
     bare construction (→ TypeVar defaults), dynamic flags, positional calls,
     **and preserves explicit parametrization** (`IntegerField[int, int]()` stays `[int, int]`).
  `<ST>`/`<GT>` are the class's own TypeVar defaults;
  `db_default: ... | _ST_X` gets the concrete `| None` union substituted in overload 1.
  - A 3rd "plain concrete-self" overload was tried and dropped:
    its `self: C[<ST>, <GT>]` overrode users' explicit `C[A, B]()` params (widening the set type).
    The 2-overload form is simpler and preserves them.
  - A `primary_key=Literal[True]` overload was also tried and dropped — the project's semantics
    (see `test_create.yml`) are "pk accepts `None` on write only when it's an AutoField **or**
    `primary_key=True` + `default=`", which is inherently plugin/`default=`-aware.
    `primary_key=True` now falls to the fallback (no `None`);
    AutoField None comes from the plugin (`fill_field_defaults(is_set_nullable=True)`),
    pk+default from the plugin's `set_descriptor_types_for_field`.
- No `__new__` anywhere (mypy #12045: `__init__` in the MRO disables `__new__` inference;
  and mypy/zuban skip `__init__` arg checking when `__new__` matches).
- Strip-only (no overloads, `null: bool`): JSONField, FilePathField (Any params);
  FileField/ImageField (FileDescriptor.__get__ never returns `None` — the plugin explicitly skips FileField);
  ArrayField, gis, range fields.
- AutoFields: `_ST_Auto` default stays `int | str` (no `| None`); the plugin adds `None` to the set type
  for AutoField pks (clone idiom / `create(id=None)`) via `fill_field_defaults(is_set_nullable=True)`.
  (Widening the default itself was tried and reverted — it leaked `| None` into every FK `_id` column.)
- Related fields (FK/O2O/M2M): stripped to 2-param, nullability stays plugin-driven.
  Extending self-annotations there needs TypeVar-parameterized self (`self: ForeignKey[_M | None]`) —
  historically unsupported by pyright, must be validated separately before stub-side adoption.
- Plugin: `set_descriptor_types_for_field` folds `None` into set/get
  (null → both; pk+`default=` → set only) but **only for "direct" fields** whose own params are their
  Field set/get types.
  Wrapper fields like `ArrayField` (params are element types) are detected via `get_field_type_args`
  and left unchanged. `_NT` slot logic deleted.

## Comparison: `_NT` (PR #3317) vs `__init__` overloads (this branch)

Checker names below refer to the current pins (mypy 1.19, pyright 1.1.411, ty 0.0.55, pyrefly) plus zuban.

| Criterion | `_NT` third TypeVar (PR #3317) | `__init__` overloads (this branch) |
|---|---|---|
| Encoding | `Field[_ST, _GT, _NT]`; `__get__` switches on `_NT` | `Field[_ST, _GT]`; 2 `__init__` overloads per field |
| `Field()` reads non-null (hard req) | yes, all 5 (`default=Any` variant: pyright only) | yes, all 5 |
| `Field(null=True)`, direct fields (hard req) | yes, all 5 (ty re-verified) | all but ty >=0.0.40 (silent solver bug) |
| Bare custom subclass `F()` (hard req) | yes | yes |
| Bare custom subclass `F(null=True)` | hard error outside mypy | accepted; reads non-null outside mypy (recipe fixes) |
| Scales to pk/default/db_default (hard req) | new TypeVar slot each, combinatorial | linear (pk stays plugin-side) |
| Bare `Field` annotation (soft req) | becomes 3-param (`AnyField` export question) | unchanged `Field[Any, Any]` |
| `Field[A, B]` annotations (soft req) | become non-null → nullable ones break | unchanged; `C[A, B]()` preserved |
| Spec footing | pyright-only param-default binding; stub ignores | standardized; typeshed `dict.__init__` precedent |
| Wrapper-field column nullability (ArrayField) | expressible (slot is orthogonal) | not expressible (see below) |
| Reveal / assert_type churn for users | every field type becomes 3-param | none vs master (2-param) |
| Stub verbosity | +1 slot on every class/alias + get/set switching | kwarg list duplicated in 2 overloads per field |
| Plugin reliance | required for custom subclasses to type-check | precision only; stubs alone never false-error |

Summary: measured against the `t.md` requirements, overloads win or tie everywhere except wrapper-field
column nullability (and direct-field `null=` on *today's* ty, until the regression is fixed upstream).
The failure modes also differ in kind: where `_NT` falls short it breaks user code loudly
(annotations, every bare custom field with `null=True`), where overloads fall short they degrade silently
to master's current behavior.
And the residual gaps differ too: `_NT`'s need spec evolution to become legal (python/typing#2213 et al.),
the overloads' one gap is a bisected ty bug with a 10-line repro and four checkers agreeing against it.

## Why not declare-once overloads on `Field` (researched 2026-07)

Question: can the overload pair live ONLY on `Field`, with subclasses inheriting the `null=True`
narrowing automatically? Answer: **no — structurally impossible on every current checker, including mypy.**
Verified empirically on mypy 2.2.0 / pyright 1.1.411 / ty 0.0.58+0.0.59 / pyrefly 1.1.1 / zuban 0.9.0
with `.pyi` + test-file repro pairs. The key case is a generic-preserving subclass with its own
PEP 696 defaults and **no** `__init__`:

```python
class IntField(Field[_ST_I, _GT_I]): ...   # _ST_I default int | float, _GT_I default int
IntField(null=True)                        # want: IntField[int | float | None, int | None]
```

Formulations tried and their per-checker results on that case:

| Formulation | mypy | pyright | ty | pyrefly | zuban |
|---|---|---|---|---|---|
| F1: class-scoped tvars in self (`self: Field[_ST \| None, _GT \| None]`) | fallback non-null (base class alone works) | unsolved `_ST@Field \| None` | `IntField[None, None]` (contravariant → `Never`) | `Unknown \| None` | **base** defaults + None (wrong types) |
| F2: function-scoped tvars w/ own defaults in self (spec-blessed form) | fallback | unsolved | fallback | **base** defaults + None | **base** defaults + None |
| F3: function-scoped tvars whose `default=` references the class tvars | fallback | unsolved | fallback | **base** defaults + None | **base** defaults + None |
| F5: metaclass `__call__` overloads | hard error (uses `object.__init__`) | fires but erases class identity (`Field[None, None]`) | erases identity | erases identity | hard error |
| F6: `__init__` declared as overloaded-Protocol attribute | constructor becomes `Any` | ignored | ignored | ignored | ignored |

Why it can't work: producing `IntField[<subclass defaults> | None]` from an inherited overload requires
the checker to substitute the *subclass* tvars into the inherited self annotation (F1) or into the
method-tvar default chain (F3) and then apply the *subclass's* defaults. No checker implements either
step — mypy/pyright silently fall back (safe), pyrefly/zuban substitute nothing and leak the *base*
defaults (actively wrong), ty's contravariant bug turns F1 into all-`None` types.

The typing spec settles the class-scoped form as non-standard, not merely unimplemented
([constructors.html#init-method](https://typing.python.org/en/latest/spec/constructors.html#init-method)):
"Class-scoped type variables should not be used in the `self` annotation … Type checkers should report
an error". mypy's partial (base-class-only) support of F1 is the off-spec behavior
(pyright discussion #9954, erictraut: "Mypy isn't following the typing spec in this regard, whereas
pyright is"). The spec-legal form (function-scoped tvars in self) solves only from *call arguments*
— and `null=True` carries no information about `_ST`/`_GT` — or from the method tvar's own fixed
defaults, which by construction can't be the subclass's. So per-class overloads are required by the
type system as it stands.

An ecosystem survey (2026-07: SQLAlchemy 2.0, pydantic v2, SQLModel, attrs, ormar, tortoise-orm,
piccolo, django-types, typeshed peewee, peewee-aio, django-enum, prisma-client-py, django-autotyping)
found **no project with a declare-once mechanism**. Everyone falls into four buckets:
annotation-driven typing where the kwarg is statically inert (SQLAlchemy `Mapped[str | None]`,
pydantic, SQLModel, attrs, ormar); per-class overload duplication on `null: Literal[True]` via
self-annotated `__init__` (tortoise-orm — same mechanism as this branch) or `__new__` (django-types,
typeshed peewee, peewee-aio, django-enum); function facades lying about the class
(zmievsa/tortoise-orm-stubs); or codegen (prisma-client-py, django-autotyping — which *generates*
per-class overload stubs rather than sharing them). Piccolo doesn't model nullability statically at
all. The only technique found that this branch didn't already use is typeshed-peewee's shared-kwargs
`Unpack[TypedDict]` — adopted as F4 below.

## Boilerplate shrink: `Unpack[TypedDict]` kwarg factoring (F4, validated 2026-07)

The overload *pair* must stay per-class, but the ~25 shared kwargs can be factored into one generic
TypedDict + PEP 692 `Unpack`, cutting each concrete field from ~60 lines to ~10 and shrinking the
README custom-field recipe likewise:

```python
class _FieldInitKwargs(TypedDict, Generic[_DB], total=False):
    primary_key: bool
    db_default: _DB          # generic member keeps db_default precise per overload
    ...                      # all kwargs shared by every field

class CharField(Field[_ST_Char, _GT_Char]):
    @overload
    def __init__(
        self: CharField[str | int | None, str | None],
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        *,
        null: Literal[True],
        **kwargs: Unpack[_FieldInitKwargs[str | int | None]],
    ) -> None: ...
    @overload
    def __init__(
        self,
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        *,
        null: bool = ...,
        **kwargs: Unpack[_FieldInitKwargs[_ST_Char]],
    ) -> None: ...
```

**The TypedDict must be `closed=True` (PEP 728).** With an *open* TypedDict, ty deliberately accepts
unknown keys through `**kwargs: Unpack[...]` ("open TypedDicts implicitly allow extra items as
`object`" — documented in ty's own mdtest `typed_dict.md`, adopted in ruff#25628/#25591, 2026-06;
mypy/pyright/pyrefly/zuban reject unknown keys either way). With `closed=True`, ty emits
`unknown-argument` and **all five checkers are fully proper**: misspelled kwargs rejected *through*
the Unpack (mypy keeps its "did you mean null?" hint and expands the TypedDict inline in overload
notes), wrong-typed kwargs caught, explicit `CharField[bytes, bytes]()` parametrization preserved,
bare subclasses degrade exactly as before. ty's only remaining deviation is its pre-existing
contravariant-self regression, identical to the non-Unpack form — F4 is never worse than the current
shape on any checker. Prior art: **typeshed's peewee stubs** use exactly this pattern (per-class
`__new__` overload pairs on `null:` + shared `**kwargs: Unpack[_FieldKwargs]`, layered subclass
TypedDicts like `_FKKwargs(_FieldKwargs)`).

Remaining caveats:

- A TypedDict member may not share a name with an explicit parameter (mypy `[misc]` def-site error),
  so `verbose_name`/`name` stay explicit params; per-class kwargs (`max_length`, `db_collation`, …)
  also stay explicit in that class's overloads.
- TypedDict members become keyword-only while Django's runtime accepts them positionally —
  positional calls beyond `verbose_name`/`name` would newly error (exotic).
- **stubtest does not expand `Unpack[TypedDict]`** (sees a bare `**kwargs`): each converted class
  needs one allowlist line for its `__init__` (name-based entries silence the whole function, so
  stubtest stops checking those signatures for runtime drift — mitigated by the TypedDict being the
  single place a new Django kwarg lands). Verified with a minimal stubtest probe; a variant keeping
  the fallback overload fully explicit still errors (`runtime does not have **kwargs`), so the
  allowlist cost is identical and full factoring wins.
- If the README recipe uses the shared TypedDict, it needs a runtime-importable home
  (`django_stubs_ext`), since user code can't import from stubs at runtime. Runtime
  `TypedDict(..., closed=True)` needs typing-extensions >=4.10 (repo already floors 4.11).

## Known limitation: wrapper-field column nullability

`ArrayField` (and similar wrapper fields) parametrize on **element** types
(`ArrayField[_ST_Array, _GT_Array]` extending `Field[Sequence[_ST_Array] | Combinable, list[_GT_Array]]`),
so without `_NT` neither the stubs nor the plugin can fold column-level `| None`:
`ArrayField(IntegerField(), null=True)` reads `list[int]` (not `list[int] | None`) and rejects `x = None`
on assignment — on **every** checker.
This is a regression vs both the `_NT` parent branch *and* master for mypy users
(master's plugin wraps `Optional` around the fully-mapped get type, so it produced `list[int] | None`);
pyright/ty/pyrefly never tracked it.
Tests flag it with TODOs (`test_array.py`, `test_meta_options.yml`).
Folding `None` into the element slot is wrong (`list[int | None]` means nullable *elements*, i.e.
`null=True` on the *base_field*), and the column type is not expressible through the element TypeVars.
Candidate follow-ups:

- Narrow per-wrapper marker: reintroduce an `_NT`-like slot **only** on wrapper fields — their params are not
  `Field`'s params, so the annotation-poisoning argument against a global `_NT` does not apply there.
- Redesign wrapper params to column level (`ArrayField[Sequence[E] | Combinable, list[E]]`), derived from
  `base_field: Field[E_ST, E_GT]` via method-scoped TypeVars in the `__init__` self-annotation.
  Same pyright/ty "TypeVar'd self" risk as the FK follow-up; breaks element-style `ArrayField[A, B]` annotations.
- Plugin special-case for mypy only: restore master parity by synthesizing `list[...] | None` descriptor types
  for wrapper fields (cheapest; keeps the plugin-hook quality bar, but grows the plugin this PR shrinks).

## ty >=0.0.40 regression (found 2026-07 after rebasing onto master)

The design was validated on ty 0.0.35 (the pin at the old branch base).
Master now pins ty 0.0.55, and ty's generics-solver overhaul in 0.0.40 broke solving a class TypeVar from a
concrete-`self` `__init__` annotation **whenever that TypeVar is contravariant** — i.e. every `Field` (`_ST`):

- Bisect: 0.0.39 good → 0.0.40 bad; still broken on 0.0.58 (current pin) and 0.0.59 (latest, re-verified 2026-07-13).
  Suspected cause: "Fix many issues in the generics solver by using constraint sets more widely to solve
  type variables" (astral-sh/ruff#24540, in the 0.0.40 release notes).
- Trigger is contravariance alone: covariant/invariant TypeVars (any arity, with or without PEP 696 defaults)
  still solve — which is why typeshed's `dict.__init__` (invariant) doesn't catch it.
  Overloads aren't needed either; the non-overloaded error message exposes the mechanism:
  ty resolves the unconstrained contravariant TypeVar to `Never` and *then* checks the `self` annotation,
  instead of solving `_T` from it (`F[_T] <: F[str | None]` with contravariant `_T` yields the lower-bound
  constraint `str | None <: _T`, satisfiable by `_T = str | None`; `Never` is the one choice that can't work).
- Effect on the stubs: `Field(null=True)` silently falls back to the `null: bool` overload → reads lose
  `| None`, `= None` writes rejected, on ty only (mypy/pyright/pyrefly/zuban unaffected).
  The README custom-field recipe (fallback with `null: Literal[False]`) hard-errors on ty for *any* construction.
- Handling: correct expectations kept in assert_type tests, suppressed per line with
  `# ty: ignore[...] # regressed in ty >=0.0.40` (test_base.py, test_custom_fields.py,
  direct_field_null_true_does_not_trigger_nullability_check/models.py).
- Follow-up: report upstream to astral-sh/ty with the repro below, then drop the ignores once fixed
  (ty flags them as unused).

### Upstream repro (for the astral-sh/ty issue)

```python
from __future__ import annotations

from typing import Generic, TypeVar, reveal_type

_T = TypeVar("_T", contravariant=True)


class F(Generic[_T]):
    def __init__(self: F[str | None]) -> None: ...


reveal_type(F())  # expected: F[str | None]
```

- ty <=0.0.39: `F[str | None]` — agrees with mypy 1.19 (`--strict`, 0 errors), pyright 1.1.411, pyrefly, zuban.
- ty >=0.0.40 (incl. 0.0.56): reveals `F[_T@F]` and errors with `invalid-argument-type`:
  "Argument to `F.__init__` is incorrect: Expected `F[str | None]`, found `F[Never]`".
- Make `_T` covariant (or invariant) and it solves fine on all versions.
- Overloaded form (the stubs' actual shape — concrete-`self` + `null: Literal[True]` overload with a
  plain-`self` fallback): same root cause, but surfaces as `no-matching-overload` when every overload has a
  concrete `self`, or as a *silent* wrong pick of the fallback overload when one exists —
  that's how it degrades `Field(null=True)` here.

## Greenday trial (2026-07-13, greenday branch `test/django-stubs-pep696-field-init-overloads`)

Method: master-baseline silenced with silence-lint-error, then branch installed;
three-way diff (master → branch-HEAD → branch+F4), cold-cache verified.

- **F4 (Unpack factoring) delta: exactly 1 new error** on 8837 files, and it's a plugin
  deferral-order edge, not a typing change: one FK's synthesized `_id` attr resolves to `Any`
  in the full-run module order (a targeted probe of the same attr reveals `str | None` correctly).
  Likely triggered by the new `django.db.models.fields → django_stubs_ext.fields` import edge
  shifting module processing order. Worth a look during review; not a blocker.
- **Branch-vs-master delta (pre-existing, NOT from F4): 249 errors**, families:
  1. Custom fields forwarding TypeVars **without PEP 696 defaults**
     (`class PlusPlusCharField(models.CharField[_ST_contra, _GT_co])`) → `Need type annotation`
     [var-annotated] on every use. This is the documented README constraint — downstream must add
     `default=` to forwarded TypeVars.
  2. Nullable FK set types missing `| None` in model-kwarg checks
     (`got "X | None", expected "X | Combinable"`) — needs plugin-side investigation.
  3. `ImageFieldFile` vs `ImageField[Any, ImageFieldFile]` arg-type mismatches.
  4. A batch of newly-unused `type: ignore` comments (errors that disappeared; verify they're
     improvements, not lost true positives).
- **Plugin API breakage for downstream custom plugins**: `get_field_descriptor_types` is gone
  (replacement: `helpers.fill_field_defaults` + `helpers.get_field_type_args` — simpler, no
  None-stripping needed) and `DjangoContext.get_field_nullability` lost its second parameter.
  Greenday's `custom_mypy_django_plugin.py` was adapted on the test branch as the migration example.

## Custom field recipes (README)

- Bare subclass `class HTMLField(TextField): ...`: works; `null=True` precise on mypy (plugin),
  degrades to non-null reads on pyright/ty/pyrefly.
  Concrete-bound `class F(Field[A, B])` is non-generic → `null=` not tracked anywhere.
- Cross-checker nullable: redeclare params with `| None` (`HtmlField[str | None, str | None]()`),
  or add 2 `__init__` overloads with `**kwargs: Unpack[FieldInitKwargs[...]]`
  (README "null=True on a custom field").

## Why not `__new__` (history, researched 2026-06)

django-types' founding design (Nov 2020, commit `64a5b3b`) was exactly this `__init__` pattern;
mypy handled it since ≤0.790.
It switched to `__new__` (PR #97, Feb 2022) because 2020-2022 pyright called self-annotated `__init__`
"an undocumented (and unspecified) typing feature" (erictraut, pyright #1211/#1550/#2909)
and mypy #12045 made the `__new__`+`__init__` combo unworkable.
Constructor inference from self-annotated `__init__` overloads has since been standardized and is
load-bearing in typeshed — all five checkers pass it today (modulo the ty regression above).
The `__new__` route was re-evaluated during this investigation and rejected on its own defects:

- mypy #12045: any `__init__` in the MRO disables `__new__`-based inference,
  so mixing the two styles across the field hierarchy is fragile.
- mypy and zuban skip `__init__` argument checking whenever a `__new__` overload matches,
  so a catch-all `__new__` silently turns off kwarg validation.
- Inherited `__new__` overloads return the *parent* class (`-> IntegerField[...]`),
  erasing subclass identity: `x: MyField = MyField()` fails on pyright/ty/pyrefly
  (mypy ignores inherited `__new__` and the plugin rescues it, but that is mypy-only).
- PR #3317's own matrix: only 🟠 "works with explicit `__new__` overrides on every custom field" on
  mypy/pyright/ty (zuban with a false positive) — i.e. every user subclass must redeclare the machinery.
In-house precedent for the `__init__` pattern: django-stubs PR #1900 (Viicos, Jan 2024, open);
it stalled on verbosity, not checker support.
PEP 696 floor: mypy 1.9.0 (1.8 ignores defaults gracefully).

## Lint note

assert_type fixtures need single-line per-checker ignore comments (so each checker's directive lands on the
line it reports the error — pyright reports on the call line, pyrefly/ty on the arg line;
only single-line covers all).
These exceed 120 chars, so `# fmt: skip` keeps ruff-format from wrapping them and
`tests/assert_type/**/*.py` ignores `E501` in `pyproject.toml`.

## Status / TODO

- [x] Base Field machinery, IntegerField + CharField exemplars
- [x] Sibling stub files stripped (related/files/json/postgres/gis/...)
- [x] Plugin conversion
- [x] Remaining concrete classes in fields/__init__.pyi
- [x] Test-suite expectation updates (assert_type + yml)
- [x] Full verification: mypy self-check, pyright/ty/pyrefly suites, pytest, stubtest (green 2026-07,
      post-rebase, with the ty ignores above)
- [ ] Report the ty >=0.0.40 contravariant-self regression upstream (repro above).
      Tracker searched 2026-07-13: no existing issue. File new, referencing ty#3277 (invariant
      sibling, fixed by ruff#24698 — fix doesn't cover contravariant), ty#2799 (open root-cause:
      constraint solver combines specializations via union), and ruff#24540 (the 0.0.40 solver
      overhaul that introduced it).
- [x] ~~Report the ty `Unpack[TypedDict]` unknown-kwarg gap upstream~~ — not a bug: deliberate ty
      semantics for *open* TypedDicts (implicit `extra_items=object`, ruff#25628); resolved on our
      side by `closed=True` (see F4 section). Optionally file a spec-conformance question — mypy,
      pyright and pyrefly all reject unknown keys for open TypedDicts per PEP 692.
- [ ] Wrapper-field column nullability: pick one of the three candidate follow-ups above
- [ ] Follow-up: FK/O2O/M2M self-annotation feasibility (pyright TypeVar'd self),
      `Combinable` placement audit
- [x] Greenday real-codebase trial (see "Greenday trial" section; F4 delta = 1 deferral-order
      error, 249 pre-existing branch deltas to review)
