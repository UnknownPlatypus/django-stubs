# PEP 696 TypeVar Defaults for Django Model Fields — Research Summary

## The Proposal

[Issue #1264](https://github.com/typeddjango/django-stubs/issues/1264) proposes replacing the mypy-plugin-specific `_pyi_private_set_type` / `_pyi_private_get_type` attributes on field classes with **PEP 696 `TypeVar(default=...)`** parameters, enabling non-mypy type checkers (pyright, pyrefly, ty) to infer field types without a plugin.

The key evolution comes from [finlayacourt's comment](https://github.com/typeddjango/django-stubs/issues/1264#issuecomment-2864346111): add a **third type variable `_NT`** to `Field` encoding nullability as `Literal[True]` or `Literal[False]`, with overloaded `__get__`/`__set__` on the base `Field` class — avoiding per-subclass overloads:

```python
_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])

class Field(Generic[_ST, _GT, _NT]):
    @overload
    def __get__(self: Field[_ST, _GT, Literal[False]], instance: Model, owner: Any) -> _GT: ...
    @overload
    def __get__(self: Field[_ST, _GT, Literal[True]], instance: Model, owner: Any) -> _GT | None: ...
```

[UnknownPlatypus confirmed](https://github.com/typeddjango/django-stubs/issues/1264#issuecomment-4164574039) this now works in **mypy 1.16+, pyright, pyrefly**, and nearly in **ty**.

---

## Issues & PRs That Would Be Superseded

| # | Title | Type | Status | Impact |
|---|-------|------|--------|--------|
| [#1900](https://github.com/typeddjango/django-stubs/pull/1900) | Add explicit overload to `Field` subclasses | PR | Open | **Superseded** — added `__new__` overloads per-subclass; `_NT` approach avoids this entirely |
| [#2590](https://github.com/typeddjango/django-stubs/pull/2590) | Feat/builtin models types | PR | Open | **Superseded or needs rework** — implements PEP 696 for `_ST`/`_GT` but lacks `_NT` nullability |
| [#2214](https://github.com/typeddjango/django-stubs/pull/2214) | Add type hints to builtin models' fields | PR | Open | **Partially superseded** — explicit annotations become unnecessary with PEP 696 defaults |
| [#2676](https://github.com/typeddjango/django-stubs/issues/2676) | Migrate `_pyi_private_set/get_type` to TypeVar defaults | Issue | Closed (dup) | Exact duplicate of #1264 |
| [#2835](https://github.com/typeddjango/django-stubs/pull/2835) | fix: Nullable field generic get type parameter should be optional | PR | Closed | **Superseded** by `_NT` approach |

## Issues That Would Be Resolved

| # | Title | Type | Status |
|---|-------|------|--------|
| [#1264](https://github.com/typeddjango/django-stubs/issues/1264) | Feature: Use PEP 696 defaults for fields | Issue | Open |
| [#579](https://github.com/typeddjango/django-stubs/issues/579) | Use django-stubs with type checkers other than mypy | Issue | Open (partially resolved) |
| [#766](https://github.com/typeddjango/django-stubs/issues/766) | `MyField(models.CharField)` not handled as `str` | Issue | Open |
| [#2724](https://github.com/typeddjango/django-stubs/issues/2724) | DateTimeField is nullable but generic get type not optional | Issue | Open |
| [#711](https://github.com/typeddjango/django-stubs/issues/711) | Field type is Any (pyright) | Issue | Closed |
| [#2534](https://github.com/typeddjango/django-stubs/issues/2534) | django-stubs causes VSCode to infer field types as Any | Issue | Closed |
| [#2043](https://github.com/typeddjango/django-stubs/issues/2043) | Custom fields with overwritten constructors don't change types based on attributes | Issue | Open (partially) |
| [#285](https://github.com/typeddjango/django-stubs/issues/285) | Inheritance from model fields | Issue | Closed |
| [#545](https://github.com/typeddjango/django-stubs/issues/545) | Custom field typing | Issue | Closed |
| [#68](https://github.com/typeddjango/django-stubs/issues/68) | Requiring field annotations even though type can be inferred | Issue | Closed |

## Nullability-Specific Issues (Addressed by `_NT` Parameter)

| # | Title | Type | Status | Relationship |
|---|-------|------|--------|-------------|
| [#2724](https://github.com/typeddjango/django-stubs/issues/2724) | DateTimeField is nullable but generic get type not optional | Issue | Open | **Resolved** by native `_NT` handling |
| [#2403](https://github.com/typeddjango/django-stubs/issues/2403) | Derived ForeignKey field type "is nullable but its generic get type parameter is not optional" | Issue | Closed | **Resolved** by [#2492](https://github.com/typeddjango/django-stubs/pull/2492), but `_NT` prevents recurrence |
| [#2492](https://github.com/typeddjango/django-stubs/pull/2492) | Fix error with `null=True` and `Any` type param for `Field` types | PR | Merged | Becomes **unnecessary** with native `_NT` |
| [#2835](https://github.com/typeddjango/django-stubs/pull/2835) | fix: Nullable field generic get type parameter should be optional | PR | Closed | **Superseded** by `_NT` approach |
| [#736](https://github.com/typeddjango/django-stubs/issues/736) | CharField(blank=True) treated as nullable | Issue | Closed | `_NT` makes nullability explicit in the type system |
| [#444](https://github.com/typeddjango/django-stubs/issues/444) | values_list returns Optional for non-nullable field with default | Issue | Closed | `_NT` reduces reliance on plugin nullability logic |

## Existing Precedent (Already Merged, Enabling Work)

| # | Title | Notes |
|---|-------|-------|
| [#2104](https://github.com/typeddjango/django-stubs/pull/2104) | Remove QuerySet alias hacks via PEP 696 TypeVar defaults | **Proves the pattern works** — PEP 696 defaults already adopted for `QuerySet` |
| [#2048](https://github.com/typeddjango/django-stubs/pull/2048) | Use field generic types for descriptors | Foundation for PEP 696 field work |
| [#2492](https://github.com/typeddjango/django-stubs/pull/2492) | Fix error with `null=True` and `Any` type param | Plugin-level fix that becomes **unnecessary** with native `_NT` |

## Complementary Work (Not Superseded)

| # | Title | Notes |
|---|-------|-------|
| [#2776](https://github.com/typeddjango/django-stubs/pull/2776) | `Manager` with generic `QuerySet` using `TypeVar` defaults (draft, by UnknownPlatypus) | Different axis of PEP 696 adoption |
| [#863](https://github.com/typeddjango/django-stubs/issues/863) | Making QuerySet classes part of the type of Manager classes | Complementary |
| [#511](https://github.com/typeddjango/django-stubs/issues/511) | Proposal: Allow narrowing ORM fields | Orthogonal feature |

---

## Why Previous PRs Failed

| PR | Approach | Why It Stalled |
|---|---|---|
| [#1900](https://github.com/typeddjango/django-stubs/pull/1900) (Viicos) | `__init__` overloads on every subclass | +1513 lines of boilerplate; [mypy #14764](https://github.com/python/mypy/issues/14764) (overload keyword resolution bug); mypy doesn't inherit `__new__` overloads across subclasses; merge conflicts |
| [#2590](https://github.com/typeddjango/django-stubs/pull/2590) (FallenDeity) | PEP 696 defaults + `__new__` overloads for null | 56 duplicate `__new__` definitions; had to replace `Field.__init__` with `*args, **kwargs` (losing parameter validation); unresolved design disagreement about null handling; merge conflicts |
| [#2214](https://github.com/typeddjango/django-stubs/pull/2214) (flaeppe) | Manual explicit generic annotations on all builtin model fields | Considered "ugly" by intgr; superseded by the PEP 696 defaults idea; author ran out of time |

---

## Maintainer Positions (Critical for Getting Merged)

### sobolevn (lead maintainer)

- **"We should not modify type params in the plugin, ever. It is hard, pretty unstable, error-prone."** — Any solution that requires the plugin to mutate TypeVar params will be rejected.
- Prefers **errors over silent patching**: `CharField[str, str](null=True)` should error, not silently widen to `str | None`. The `_NT` approach satisfies this — the type is correct by construction.
- Found `strict_optional = False` edge cases "very niche" — focus the PR on the mainstream `strict_optional = True` case.
- Style preferences: `_` prefix on `@type_check_only` classes, TypeVars placed near their usage, annotation style (`: models.AutoField`) preferred over assignment style (`= models.AutoField()`).

### intgr

- Called explicit generic annotations on every field "quite ugly" — pushed for PEP 696 defaults.
- Argued against a 3rd TypeVar for `WithAnnotations` (real solution is `Intersection` types, tracked at [python/typing#213](https://github.com/python/typing/issues/213)).

### flaeppe

- Identified [mypy #14764](https://github.com/python/mypy/issues/14764) (overload resolution with keyword arguments) as a potential blocker for overload-based approaches. Worth verifying whether `_NT` is affected.
- Preferred error-on-mismatch over silent type patching.

---

## Tricky Field Types to Watch For

- **ForeignKey / OneToOneField**: flaeppe got stuck on [mypy #14764](https://github.com/python/mypy/issues/14764) with these. They live in `related.pyi` and were NOT included in PR #1900. Need special attention.
- **ManyToManyField**: Cannot be explicitly annotated — the 2nd type param is a synthetic through-model class that doesn't exist at runtime. Need `@type_check_only` through-model classes (e.g., `_Group_permissions`, `_User_groups`).
- **GIS fields**: Have **4 type parameters** (`_ST`, `_GT`, `_Form_ClassT`, `_GEOM_ClassT`), making them much more verbose. Each concrete GIS field needs its own set of TypeVars with defaults.
- **AutoField / BigAutoField**: `_ST` must accept `None` because they can be omitted on creation (auto-increment). Primary key + default logic is special-cased in the plugin.
- **Custom fields with `*args, **kwargs` passthrough**: The `_NT` approach partially helps, but if a custom field overrides `__init__` with `(*args, **kwargs)`, the `null` parameter is swallowed into `**kwargs` and overloads don't propagate. This affects most third-party fields (`django-money`, `django-phonenumber-field`, etc.). Manual `_NT` parameterization is the escape hatch.
- **AbstractBaseSession.pk**: `pk` is `CharField` (session_key is PK), not `AutoField` — don't assume `pk` is always `int`.
- **NullBooleanField**: Inherently nullable, needs `None` in both set/get types regardless of `null=`.
- **DecimalField / FilePathField**: Override `__init__` with extra params (`max_digits`, `decimal_places`, `path`, etc.) — if overloads are needed on subclasses, these params must be duplicated.

---

## Stubtest Complications

Any approach that types model fields will cause **stubtest failures** because at runtime `Model.field` returns a `DeferredAttribute`, not the annotated field type. [PR #2590](https://github.com/typeddjango/django-stubs/pull/2590) established a pattern: create a dedicated category in `allowlist.txt` for model field annotations. Budget for this.

Making `null` a `Literal[True] | Literal[False]` type also fails stubtest (runtime signature is just `bool`). [PR #1900](https://github.com/typeddjango/django-stubs/pull/1900) added allowlist entries like:

```
django.db.models.(\w*)Field.__init__
```

---

## Established Patterns to Reuse (from merged PR #2104)

[PR #2104](https://github.com/typeddjango/django-stubs/pull/2104) (PEP 696 for QuerySet) is the direct precedent:

- Use `typing_extensions.TypeVar` with `default=` (project already requires `typing-extensions>=4.11.0`)
- Keep deprecated aliases as `TypeAlias = NewName`
- Update `mypy_django_plugin/lib/fullnames.py` when renaming classes
- Add `reveal_type` test cases verifying default expansion
- Expect minimum mypy version bump ([PR #2104](https://github.com/typeddjango/django-stubs/pull/2104) required mypy >= 1.10; the `_NT` approach needs mypy >= 1.16)
- Always handle `AnyType` and `UninhabitedType` (Never) when resolving generic params through MRO

---

## mypy Bugs to Verify Are Fixed

Before proceeding, verify these are resolved in mypy 1.16+:

- [python/mypy#14764](https://github.com/python/mypy/issues/14764) — overload resolution with keyword arguments (flagged by flaeppe as blocker for related fields)
- [python/mypy#14851](https://github.com/python/mypy/issues/14851) — TypeVar defaults in generic classes (flagged by flaeppe as potential issue)
- [python/mypy#5146](https://github.com/python/mypy/issues/5146) — `__new__` overload inheritance (the `_NT` approach avoids `__new__` entirely but inherited `__get__`/`__set__` overloads must resolve correctly)
- **Inherited `self`-typed overloads through descriptor protocol** — finlayacourt's finding that mypy didn't resolve inherited `__get__` overloads. [UnknownPlatypus confirmed](https://github.com/typeddjango/django-stubs/issues/1264#issuecomment-4164574039) mypy 1.16+ fixes this, but worth double-checking.

---

## The `django-types` Fork as Prior Art

The competing [`django-types`](https://github.com/sbdchd/django-types) package already uses `__init__` overloads with `Literal` to handle nullable fields purely through stubs. Several commenters referenced it as proof-of-concept. Worth studying their implementation at `django-types/django-stubs/db/models/fields/__init__.pyi` for patterns, but the `_NT` approach is strictly cleaner (overloads only on the base class).

---

## Bottom Line

The `_NT` approach elegantly resolves the issues that sank all three previous PRs — no per-subclass overloads, no plugin type mutation, nullability correct by construction. The main risks are:

1. **Confirming mypy 1.16+ truly handles inherited descriptor overloads** (verified by UnknownPlatypus but worth double-checking)
2. **ForeignKey/M2M fields needing special attention** (flaeppe's mypy #14764 concern)
3. **Getting buy-in from sobolevn on the design before writing too much code**

Recommended approach: open a discussion or draft PR with a minimal proof-of-concept (base `Field` + `CharField` + `IntegerField` + one FK field) to get maintainer feedback early.
