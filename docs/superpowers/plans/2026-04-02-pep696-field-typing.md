# PEP 696 TypeVar Defaults for Field Typing — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `_pyi_private_set_type` / `_pyi_private_get_type` class attributes with PEP 696 TypeVar defaults and a null-aware `_NT` TypeVar, making field typing work across all type checkers (mypy, pyright, pyrefly, ty) without requiring a plugin for basic field get/set descriptor resolution.

**Architecture:** Add a third generic parameter `_NT` (constrained to `Literal[True] | Literal[False]`, default `Literal[False]`) to the `Field` base class. Overloaded `__get__`/`__set__` methods on `Field` dispatch on `_NT` to add `| None` when the field is nullable. Each field subclass uses PEP 696 TypeVar defaults to declare its base set/get types (replacing `_pyi_private_*`). The mypy plugin is updated to read types from the resolved generic args (which now include defaults) instead of private class attributes.

**Tech Stack:** Python type stubs (.pyi), mypy plugin API (`TypeVarType.default`, `map_instance_to_supertype`), typing_extensions

**Context links:**
- Issue: https://github.com/typeddjango/django-stubs/issues/1264
- Comment with approach: https://github.com/typeddjango/django-stubs/issues/1264#issuecomment-2864346111
- Research: `research-pep696-fields.md` (superseded issues, maintainer positions, tricky fields)
- Prior art: `django-types` package already uses `__init__` overloads with `Literal` for nullable fields
- Verified working: mypy 1.20, pyright 1.1.408, pyrefly, ty (see prototype at `/tmp/test_nt_advanced.py`)

**Supersedes:** PRs #1900, #2590, #2214; resolves issues #1264, #579 (partially), #766, #2724

**Key maintainer position (sobolevn):** *"We should not modify type params in the plugin, ever. It is hard, pretty unstable, error-prone."* — The plugin must NOT call `copy_modified(args=...)` for basic fields. Let the stubs handle typing; the plugin only intervenes for related fields (FK/O2O/M2M) and ArrayField.

---

## Prerequisites

Before starting implementation:

- [ ] **Bump minimum mypy version** in `pyproject.toml` from `mypy>=1.13` to `mypy>=1.16` — inherited descriptor overloads require mypy 1.16+ ([confirmed by UnknownPlatypus](https://github.com/typeddjango/django-stubs/issues/1264#issuecomment-4164574039))
- [ ] **Verify mypy #14764** (overload resolution with keyword args) is fixed in mypy 1.16+ — flaeppe flagged this as a blocker for ForeignKey. Write a quick test with `ForeignKey(to=Model, on_delete=CASCADE, null=True)` and verify `__get__` resolves correctly.
- [ ] **Verify inherited `self`-typed overloads through descriptor protocol** — finlayacourt found mypy didn't resolve inherited `__get__` overloads in subclasses. UnknownPlatypus confirmed 1.16+ fixes this, but double-check with `IntegerField(null=True)` on a model.

---

## File Map

### Stubs to modify

| File | Change | Notes |
|------|--------|-------|
| `django-stubs/db/models/fields/__init__.pyi` | Add `_NT`, modify `Field` base, convert all fields | Main work |
| `django-stubs/db/models/fields/related.pyi` | Add `_NT` threading, remove `_pyi_private_*` from FK/O2O | Related fields keep `Any` for plugin resolution |
| `django-stubs/db/models/fields/json.pyi` | Add `_NT` threading | Already uses PEP 696 defaults for `_ST`/`_GT` |
| `django-stubs/contrib/postgres/fields/array.pyi` | Add `_NT`, convert to TypeVar defaults | |
| `django-stubs/contrib/gis/db/models/fields.pyi` | Add `_NT`, convert all geometry fields | 7 concrete fields + 2 base classes |
| `django-stubs/contrib/contenttypes/fields.pyi` | Remove `_pyi_private_*` from GenericForeignKey | GFK has its own `__get__`/`__set__` |

### Plugin files to modify

| File | Change |
|------|--------|
| `mypy_django_plugin/lib/helpers.py` | Replace `get_private_descriptor_type` with TypeVar-default reader |
| `mypy_django_plugin/transformers/fields.py` | Make `set_descriptor_types_for_field` a **no-op for basic fields** (per sobolevn: "don't modify type params in the plugin"); preserve 3-arg handling for related/array fields only |
| `mypy_django_plugin/django/context.py` | Update all `get_private_descriptor_type` call sites (6 calls) |
| `mypy_django_plugin/transformers/querysets.py` | Update expression type resolution (1 call) |

### Config files to modify

| File | Change |
|------|--------|
| `pyproject.toml` | Bump `mypy>=1.13` → `mypy>=1.16` |
| `scripts/stubtest/allowlist*.txt` | Add allowlist entries for `null: _NT` vs runtime `null: bool` |

### Test files to update

| File | Change |
|------|--------|
| `tests/typecheck/fields/test_nullable.yml` | May need minor adjustments |
| `tests/typecheck/fields/test_custom_fields.yml` | Custom field generic params now 3-ary |
| `tests/typecheck/fields/test_base.yml` | Verify field types still correct |
| `tests/typecheck/fields/test_related.yml` | Verify FK/O2O types still correct |
| `tests/typecheck/fields/test_postgres_fields.yml` | Verify ArrayField types |

### Not changed (out of scope)

- `_pyi_lookup_exact_type` — kept as-is (separate concern, only used by the plugin for filter lookups)
- `django-stubs/db/models/fields/files.pyi` — FileField/ImageField have no `_pyi_private_*` attributes

---

## Task 1: Add `_NT` TypeVar and modify `Field` base class

**Files:**
- Modify: `django-stubs/db/models/fields/__init__.pyi:1-189`

This is the foundational change. Everything else builds on it.

- [ ] **Step 1: Add the `_NT` TypeVar and update the `Field` class signature**

In `django-stubs/db/models/fields/__init__.pyi`, add the `Literal` import to the existing `typing` import line, then add the `_NT` TypeVar and update `Field`:

```python
# At the top, update the typing import to include Literal (it's already there)
# After the existing _ST, _GT TypeVars (lines 48-51), add:

_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])
```

Change the class declaration from:
```python
class Field(RegisterLookupMixin, Generic[_ST, _GT]):
```
to:
```python
class Field(RegisterLookupMixin, Generic[_ST, _GT, _NT]):
```

- [ ] **Step 2: Remove `_pyi_private_set_type` and `_pyi_private_get_type` from `Field`**

Remove these three lines (112-114):
```python
    _pyi_private_set_type: Any
    _pyi_private_get_type: Any
    _pyi_lookup_exact_type: Any  # KEEP THIS ONE
```

Keep `_pyi_lookup_exact_type: Any` — it's out of scope.

Also update the docstring (lines 107-109) to remove the reference to `_pyi_private_set_type`.

- [ ] **Step 3: Change `null` parameter type in `Field.__init__`**

Change line 161 from:
```python
        null: bool = False,
```
to:
```python
        null: _NT = ...,
```

Using `...` (ellipsis) is standard for stub defaults. The TypeVar default `Literal[False]` handles the case when `null` is omitted.

- [ ] **Step 4: Add overloaded `__get__` and `__set__` with `_NT` dispatch**

Replace the current `__set__` (line 180) and `__get__` overloads (lines 181-189) with:

```python
    @overload
    def __set__(self: Field[_ST, _GT, Literal[False]], instance: Any, value: _ST) -> None: ...
    @overload
    def __set__(self: Field[_ST, _GT, Literal[True]], instance: Any, value: _ST | None) -> None: ...
    # class access
    @overload
    def __get__(self, instance: None, owner: Any) -> _FieldDescriptor[Self]: ...
    # non-null Model instance access
    @overload
    def __get__(self: Field[Any, _GT, Literal[False]], instance: Model, owner: Any) -> _GT: ...
    # nullable Model instance access
    @overload
    def __get__(self: Field[Any, _GT, Literal[True]], instance: Model, owner: Any) -> _GT | None: ...
    # non-Model instances
    @overload
    def __get__(self, instance: Any, owner: Any) -> Self: ...
```

- [ ] **Step 5: Verify the file parses correctly**

Run: `uv run python3 -c "import ast; ast.parse(open('django-stubs/db/models/fields/__init__.pyi').read())"`
Expected: No output (success)

- [ ] **Step 6: Commit**

```bash
git add django-stubs/db/models/fields/__init__.pyi
git commit -m "feat: add _NT TypeVar to Field base class for null-aware descriptors"
```

---

## Task 2: Convert basic fields in `__init__.pyi` to PEP 696 defaults

**Files:**
- Modify: `django-stubs/db/models/fields/__init__.pyi:260-710`

Each field subclass gets its own TypeVars with defaults (replacing `_pyi_private_set_type`/`_pyi_private_get_type`). Fields that only inherit from another field with no type changes just thread `_NT` through.

- [ ] **Step 1: Convert IntegerField and its subclasses**

Before `IntegerField`, add its TypeVars:

```python
_ST_INT = TypeVar("_ST_INT", contravariant=True, default=float | int | str | Combinable)
_GT_INT = TypeVar("_GT_INT", covariant=True, default=int)
```

Change `IntegerField` from:
```python
class IntegerField(Field[_ST, _GT]):
    _pyi_private_set_type: float | int | str | Combinable
    _pyi_private_get_type: int
    _pyi_lookup_exact_type: str | int
```
to:
```python
class IntegerField(Field[_ST_INT, _GT_INT, _NT]):
    _pyi_lookup_exact_type: str | int
```

Update subclasses that just inherit:
```python
class SmallIntegerField(IntegerField[_ST_INT, _GT_INT, _NT]): ...
class BigIntegerField(IntegerField[_ST_INT, _GT_INT, _NT]):
    ...
class PositiveIntegerField(PositiveIntegerRelDbTypeMixin, IntegerField[_ST_INT, _GT_INT, _NT]):
    ...
class PositiveSmallIntegerField(PositiveIntegerRelDbTypeMixin, SmallIntegerField[_ST_INT, _GT_INT, _NT]):
    ...
class PositiveBigIntegerField(PositiveIntegerRelDbTypeMixin, BigIntegerField[_ST_INT, _GT_INT, _NT]):
    ...
```

- [ ] **Step 2: Convert FloatField**

```python
_ST_FLOAT = TypeVar("_ST_FLOAT", contravariant=True, default=float | int | str | Combinable)
_GT_FLOAT = TypeVar("_GT_FLOAT", covariant=True, default=float)
```

Change:
```python
class FloatField(Field[_ST_FLOAT, _GT_FLOAT, _NT]):
    _pyi_lookup_exact_type: float
```

- [ ] **Step 3: Convert DecimalField**

```python
_ST_DECIMAL = TypeVar("_ST_DECIMAL", contravariant=True, default=str | float | decimal.Decimal | Combinable)
_GT_DECIMAL = TypeVar("_GT_DECIMAL", covariant=True, default=decimal.Decimal)
```

Change:
```python
class DecimalField(Field[_ST_DECIMAL, _GT_DECIMAL, _NT]):
    _pyi_lookup_exact_type: str | int | decimal.Decimal
    ...
```

Also update `null: bool = ...` → `null: _NT = ...` in DecimalField's `__init__`.

- [ ] **Step 4: Convert CharField and subclasses**

```python
_ST_CHAR = TypeVar("_ST_CHAR", contravariant=True, default=str | int | Combinable)
_GT_CHAR = TypeVar("_GT_CHAR", covariant=True, default=str)
```

```python
class CharField(Field[_ST_CHAR, _GT_CHAR, _NT]):
    _pyi_lookup_exact_type: Any  # objects are converted to string before comparison
    ...
```

Also update `null: bool = ...` → `null: _NT = ...` in CharField's `__init__`.

Update subclasses:
```python
class CommaSeparatedIntegerField(CharField[_ST_CHAR, _GT_CHAR, _NT]): ...

class SlugField(CharField[_ST_CHAR, _GT_CHAR, _NT]):
    ...  # update null: _NT = ... in __init__

class URLField(CharField[_ST_CHAR, _GT_CHAR, _NT]):
    ...  # update null: _NT = ... in __init__
```

For `EmailField` (narrower set type):
```python
_ST_EMAIL = TypeVar("_ST_EMAIL", contravariant=True, default=str | Combinable)

class EmailField(CharField[_ST_EMAIL, _GT_CHAR, _NT]):
    ...
```

(Remove `_pyi_private_set_type: str | Combinable` from EmailField)

- [ ] **Step 5: Convert TextField**

```python
_ST_TEXT = TypeVar("_ST_TEXT", contravariant=True, default=str | Combinable)
_GT_TEXT = TypeVar("_GT_TEXT", covariant=True, default=str)
```

```python
class TextField(Field[_ST_TEXT, _GT_TEXT, _NT]):
    _pyi_lookup_exact_type: Any
    ...  # update null: _NT = ... in __init__
```

- [ ] **Step 6: Convert BooleanField and NullBooleanField**

```python
_ST_BOOL = TypeVar("_ST_BOOL", contravariant=True, default=bool | Combinable)
_GT_BOOL = TypeVar("_GT_BOOL", covariant=True, default=bool)
```

```python
class BooleanField(Field[_ST_BOOL, _GT_BOOL, _NT]):
    _pyi_lookup_exact_type: bool
    ...
```

For `NullBooleanField`, it should default to nullable:
```python
_ST_NBOOL = TypeVar("_ST_NBOOL", contravariant=True, default=bool | Combinable | None)
_GT_NBOOL = TypeVar("_GT_NBOOL", covariant=True, default=bool | None)

class NullBooleanField(BooleanField[_ST_NBOOL, _GT_NBOOL, _NT]):
    _pyi_lookup_exact_type: bool | None  # type: ignore[assignment]
```

- [ ] **Step 7: Convert IP fields**

```python
_ST_IP = TypeVar("_ST_IP", contravariant=True, default=str | Combinable)
_GT_IP = TypeVar("_GT_IP", covariant=True, default=str)
```

```python
class IPAddressField(Field[_ST_IP, _GT_IP, _NT]): ...

_ST_GENIP = TypeVar("_ST_GENIP", contravariant=True, default=str | int | Callable[..., Any] | Combinable)

class GenericIPAddressField(Field[_ST_GENIP, _GT_IP, _NT]):
    ...  # update null: _NT = ... in __init__
```

- [ ] **Step 8: Convert date/time fields**

```python
_ST_DATE = TypeVar("_ST_DATE", contravariant=True, default=str | date | Combinable)
_GT_DATE = TypeVar("_GT_DATE", covariant=True, default=date)

class DateField(DateTimeCheckMixin, Field[_ST_DATE, _GT_DATE, _NT]):
    _pyi_lookup_exact_type: str | date
    ...  # update null: _NT = ... in __init__

_ST_TIME = TypeVar("_ST_TIME", contravariant=True, default=str | time | real_datetime | Combinable)
_GT_TIME = TypeVar("_GT_TIME", covariant=True, default=time)

class TimeField(DateTimeCheckMixin, Field[_ST_TIME, _GT_TIME, _NT]):
    ...  # update null: _NT = ... in __init__

_ST_DATETIME = TypeVar("_ST_DATETIME", contravariant=True, default=str | real_datetime | date | Combinable)
_GT_DATETIME = TypeVar("_GT_DATETIME", covariant=True, default=real_datetime)

class DateTimeField(DateField[_ST_DATETIME, _GT_DATETIME, _NT]):
    _pyi_lookup_exact_type: str | real_datetime
    ...
```

- [ ] **Step 9: Convert UUIDField**

```python
_ST_UUID = TypeVar("_ST_UUID", contravariant=True, default=str | uuid.UUID)
_GT_UUID = TypeVar("_GT_UUID", covariant=True, default=uuid.UUID)

class UUIDField(Field[_ST_UUID, _GT_UUID, _NT]):
    _pyi_lookup_exact_type: uuid.UUID | str
    ...  # update null: _NT = ... in __init__
```

- [ ] **Step 10: Convert remaining fields**

**FilePathField** (no `_pyi_private_*`, inherits from Field):
```python
class FilePathField(Field[_ST, _GT, _NT]):
    ...  # update null: _NT = ... in __init__
```

**BinaryField:**
```python
_GT_BINARY = TypeVar("_GT_BINARY", covariant=True, default=bytes | memoryview)

class BinaryField(Field[_ST, _GT_BINARY, _NT]):
    ...
```

**DurationField:**
```python
_GT_DURATION = TypeVar("_GT_DURATION", covariant=True, default=timedelta)

class DurationField(Field[_ST, _GT_DURATION, _NT]):
    ...
```

**AutoField and subclasses:**
```python
_ST_AUTO = TypeVar("_ST_AUTO", contravariant=True, default=Combinable | int | str)
_GT_AUTO = TypeVar("_GT_AUTO", covariant=True, default=int)

class AutoField(AutoFieldMixin, IntegerField[_ST_AUTO, _GT_AUTO, _NT], metaclass=AutoFieldMeta):
    _pyi_lookup_exact_type: str | int

class BigAutoField(AutoFieldMixin, BigIntegerField[_ST_AUTO, _GT_AUTO, _NT]): ...
class SmallAutoField(AutoFieldMixin, SmallIntegerField[_ST_AUTO, _GT_AUTO, _NT]): ...
```

- [ ] **Step 11: Verify the file parses and run existing tests**

Run: `uv run python3 -c "import ast; ast.parse(open('django-stubs/db/models/fields/__init__.pyi').read())"`

Run: `uv run pytest tests/typecheck/fields/test_base.yml -v --no-header 2>&1 | tail -20`

(Tests may fail at this point since the plugin hasn't been updated yet — that's expected. The goal here is to verify the stub itself is syntactically valid.)

- [ ] **Step 12: Commit**

```bash
git add django-stubs/db/models/fields/__init__.pyi
git commit -m "feat: convert all basic fields to PEP 696 TypeVar defaults"
```

---

## Task 3: Convert related fields, JSON, and contrib fields

**Files:**
- Modify: `django-stubs/db/models/fields/related.pyi`
- Modify: `django-stubs/db/models/fields/json.pyi`
- Modify: `django-stubs/contrib/postgres/fields/array.pyi`
- Modify: `django-stubs/contrib/gis/db/models/fields.pyi`
- Modify: `django-stubs/contrib/contenttypes/fields.pyi`

- [ ] **Step 1: Update `related.pyi`**

In `related.pyi`, the existing `_ST`/`_GT` TypeVars (lines 35-38) already have a PEP 696 default on `_GT`. Add the `_NT` import and TypeVar:

Add to imports:
```python
from typing import Any, Generic, Literal, TypeVar, overload
```

After existing `_ST`/`_GT` (line 38), add:
```python
_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])
```

Update the class hierarchy to thread `_NT`:

```python
class RelatedField(FieldCacheMixin, Field[_ST, _GT, _NT]):
    ...  # update null: _NT = ... in __init__

class ForeignObject(RelatedField[_ST, _GT, _NT]):
    ...  # update null: _NT = ... in __init__

class ForeignKey(ForeignObject[_ST, _GT, _NT]):
    # Remove _pyi_private_set_type and _pyi_private_get_type
    ...  # update null: _NT = ... in __init__

class OneToOneField(ForeignKey[_ST, _GT, _NT]):
    # Remove _pyi_private_set_type and _pyi_private_get_type
    ...  # update null: _NT = ... in __init__

class ManyToManyField(RelatedField[Any, Any, _NT], Generic[_To, _Through]):
    ...
```

**Note:** ForeignKey/OneToOneField keep `_ST`/`_GT` as `Any`-defaulting TypeVars because the plugin fills them in with the related model type. The `_NT` addition handles nullability.

**Warning (ManyToManyField):** M2M is the trickiest field. Its 2nd type param `_Through` is a synthetic through-model class that doesn't exist at runtime. The existing `Generic[_To, _Through]` pattern already works separately from `Field`'s generics. Threading `_NT` through `RelatedField[Any, Any, _NT]` should be safe since M2M doesn't really use `_NT` (M2M fields don't have meaningful `__get__`/`__set__` on model instances — they return managers). Verify this doesn't break existing M2M tests.

- [ ] **Step 2: Update `json.pyi`**

`json.pyi` already uses PEP 696 defaults for `_ST`/`_GT`. Just add `_NT`:

```python
from typing import Any, ClassVar, Literal, TypeVar

_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])

class JSONField(CheckFieldDefaultMixin, Field[_ST, _GT, _NT]):
    ...
```

- [ ] **Step 3: Update `array.pyi`**

```python
from typing import Any, ClassVar, Literal, TypeVar

_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])

_ST_ARRAY = TypeVar("_ST_ARRAY", contravariant=True, default=Sequence[Any] | Combinable)
_GT_ARRAY = TypeVar("_GT_ARRAY", covariant=True, default=list[Any])

class ArrayField(CheckPostgresInstalledMixin, CheckFieldDefaultMixin, Field[_ST_ARRAY, _GT_ARRAY, _NT]):
    # Remove _pyi_private_set_type and _pyi_private_get_type
    ...  # update null: _NT = ... in __init__
```

- [ ] **Step 4: Update GIS fields**

In `contrib/gis/db/models/fields.pyi`, add the `_NT` TypeVar and convert all geometry fields.

```python
from typing import Any, Literal, NamedTuple, TypeVar

_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])
```

Update base classes:
```python
class BaseSpatialField(Field[_ST, _GT, _NT]):
    ...  # update null: _NT = ... in __init__

class GeometryField(BaseSpatialField[_ST, _GT, _NT]):
    ...  # update null: _NT = ... in __init__
```

Convert each geometry field (PointField, LineStringField, PolygonField, MultiPointField, MultiLineStringField, MultiPolygonField, GeometryCollectionField). Example for PointField:

```python
_ST_POINT = TypeVar("_ST_POINT", contravariant=True, default=Point | Combinable)
_GT_POINT = TypeVar("_GT_POINT", covariant=True, default=Point)

class PointField(GeometryField[_ST_POINT, _GT_POINT, _NT]):
    _pyi_lookup_exact_type: Point  # KEEP
    geom_class: type[Point]
    form_class: type[forms.PointField]
```

Repeat the pattern for all 7 geometry fields. Also update:
```python
class ExtentField(Field[Any, Any, _NT]): ...
class RasterField(BaseSpatialField[_ST, _GT, _NT]): ...
```

- [ ] **Step 5: Update `contenttypes/fields.pyi`**

`GenericForeignKey` already defines its own `__get__`/`__set__`, so just remove the `_pyi_private_*`:

```python
class GenericForeignKey(FieldCacheMixin, Field):
    # Remove these two lines:
    # _pyi_private_set_type: Any | Combinable
    # _pyi_private_get_type: Any
    ...
```

- [ ] **Step 6: Commit**

```bash
git add django-stubs/db/models/fields/related.pyi \
        django-stubs/db/models/fields/json.pyi \
        django-stubs/contrib/postgres/fields/array.pyi \
        django-stubs/contrib/gis/db/models/fields.pyi \
        django-stubs/contrib/contenttypes/fields.pyi
git commit -m "feat: add _NT and PEP 696 defaults to related, JSON, postgres, GIS, and contenttypes fields"
```

---

## Task 4: Update mypy plugin — replace `get_private_descriptor_type`

**Files:**
- Modify: `mypy_django_plugin/lib/helpers.py:399-414`

This replaces the function that reads `_pyi_private_set_type`/`_pyi_private_get_type` with one that reads TypeVar defaults from the `Field` base.

- [ ] **Step 1: Add new `get_field_descriptor_type` function**

In `mypy_django_plugin/lib/helpers.py`, add a new function alongside the existing `get_private_descriptor_type` (do not remove it yet — we'll migrate callers first):

```python
def get_field_descriptor_type_from_typevar_default(
    type_info: TypeInfo, param_index: int, is_nullable: bool
) -> MypyType:
    """Get the set (0) or get (1) type from Field's TypeVar defaults.

    Walks the MRO to find the Field base class and reads the TypeVar default
    for the requested parameter index.
    """
    from mypy_django_plugin.lib.fullnames import FIELD_FULLNAME

    # Find Field in MRO
    field_base = None
    for base in type_info.mro:
        if base.fullname == FIELD_FULLNAME:
            field_base = base
            break
    if field_base is None:
        return AnyType(TypeOfAny.explicit)

    # Map through the inheritance chain to resolve type args
    from mypy.maptype import map_instance_to_supertype
    from mypy.types import TypeVarType

    # Use the type's own type vars as args for an unparameterized instance
    default_args: list[MypyType] = []
    for tv in type_info.defn.type_vars:
        default_args.append(TypeVarType(tv))
    instance = Instance(type_info, default_args)

    try:
        mapped = map_instance_to_supertype(instance, field_base)
    except TypeError:
        return AnyType(TypeOfAny.from_error)

    if param_index >= len(mapped.args):
        return AnyType(TypeOfAny.explicit)

    arg_type = get_proper_type(mapped.args[param_index])

    # If it's a TypeVar, use its default
    if isinstance(arg_type, TypeVarType):
        if arg_type.has_default:
            descriptor_type = get_proper_type(arg_type.default)
        else:
            return AnyType(TypeOfAny.explicit)
    else:
        descriptor_type = arg_type

    if is_nullable:
        descriptor_type = make_optional_type(descriptor_type)
    return descriptor_type
```

You need to add these imports at the top of `helpers.py` if not already present:
```python
from mypy.types import TypeVarType
```

- [ ] **Step 2: Update `get_private_descriptor_type` to delegate**

Replace the existing `get_private_descriptor_type` body to route between the old and new approaches:

```python
def get_private_descriptor_type(type_info: TypeInfo, private_field_name: str, is_nullable: bool) -> MypyType:
    """Return declared type of type_info's private_field_name (used for private Field attributes).

    For _pyi_private_set_type and _pyi_private_get_type, reads from TypeVar defaults.
    For _pyi_lookup_exact_type, reads from the class attribute (legacy approach).
    """
    if private_field_name == "_pyi_private_set_type":
        return get_field_descriptor_type_from_typevar_default(type_info, 0, is_nullable)
    elif private_field_name == "_pyi_private_get_type":
        return get_field_descriptor_type_from_typevar_default(type_info, 1, is_nullable)

    # Legacy path for _pyi_lookup_exact_type and others
    sym = type_info.get(private_field_name)
    if sym is None:
        return AnyType(TypeOfAny.explicit)

    node = sym.node
    if isinstance(node, Var):
        descriptor_type = node.type
        if descriptor_type is None:
            return AnyType(TypeOfAny.explicit)

        if is_nullable:
            descriptor_type = make_optional_type(descriptor_type)
        return descriptor_type
    return AnyType(TypeOfAny.explicit)
```

This keeps backward compatibility — all existing callers continue to work. The `_pyi_lookup_exact_type` path still reads the class attribute.

- [ ] **Step 3: Run a quick smoke test**

Run: `uv run pytest tests/typecheck/fields/test_nullable.yml -v --no-header 2>&1 | tail -20`

Check if basic nullability tests pass.

- [ ] **Step 4: Commit**

```bash
git add mypy_django_plugin/lib/helpers.py
git commit -m "feat: read field set/get types from TypeVar defaults instead of _pyi_private_*"
```

---

## Task 5: Update mypy plugin — make basic fields a no-op, preserve related/array handling

**Files:**
- Modify: `mypy_django_plugin/transformers/fields.py:52-178`
- Modify: `mypy_django_plugin/main.py` (if needed)

**Key principle (sobolevn):** *"We should not modify type params in the plugin, ever."* For basic fields, the stubs now handle everything via `_NT` + TypeVar defaults. The plugin's `set_descriptor_types_for_field` currently calls `copy_modified(args=...)` — this must stop for basic fields. The plugin should only modify type args for related fields (FK/O2O) and ArrayField, where it fills in the related model type.

- [ ] **Step 1: Make `set_descriptor_types_for_field` a no-op for basic fields**

The function `set_descriptor_types_for_field_callback` at line 131-137 is the entry point for basic (non-related, non-M2M, non-array) fields. With PEP 696 defaults + `_NT`, mypy's `ctx.default_return_type` is already correct (e.g., `IntegerField[float | int | str | Combinable, int, Literal[True]]`).

Change `set_descriptor_types_for_field_callback` to return the default return type as-is:

```python
def set_descriptor_types_for_field_callback(ctx: FunctionContext, django_context: DjangoContext) -> MypyType:
    # With PEP 696 TypeVar defaults and _NT, mypy already infers the correct
    # field type from the stubs. No plugin intervention needed for basic fields.
    return ctx.default_return_type
```

**Keep** `set_descriptor_types_for_field` itself — it's still called by `fill_descriptor_types_for_related_field` for FK/O2O fields. But update it to handle 3 type args.

- [ ] **Step 2: Update `set_descriptor_types_for_field` to handle 3 type args**

The function at line 140-178 returns `default_return_type.copy_modified(args=[set_type, get_type])`. With the new 3-arg `Field[_ST, _GT, _NT]`, this needs to preserve the `_NT` argument:

Change line 178 from:
```python
    return default_return_type.copy_modified(args=[set_type, get_type])
```
to:
```python
    # Preserve _NT (3rd arg) and any additional args, while updating _ST and _GT
    new_args: list[MypyType] = [set_type, get_type]
    if len(default_return_type.args) > 2:
        new_args.extend(default_return_type.args[2:])
    return default_return_type.copy_modified(args=new_args)
```

- [ ] **Step 3: Update `reparametrize_related_field_type` to preserve extra args**

At line 52-57:
```python
def reparametrize_related_field_type(related_field_type: Instance, set_type: MypyType, get_type: MypyType) -> Instance:
    args: list[MypyType] = [
        helpers.convert_any_to_type(related_field_type.args[0], set_type),
        helpers.convert_any_to_type(related_field_type.args[1], get_type),
    ]
    # Preserve _NT and any additional args
    if len(related_field_type.args) > 2:
        args.extend(related_field_type.args[2:])
    return related_field_type.copy_modified(args=args)
```

- [ ] **Step 4: Update `determine_type_of_array_field` to handle 3 type args**

At line 214, the assertion checks for 2 args:
```python
    assert len(base_field_arg_type.args) == len(default_return_type.args) == 2
```

Change to:
```python
    assert len(base_field_arg_type.args) >= 2 and len(default_return_type.args) >= 2
```

And at line 229, update to preserve extra args:
```python
    # Preserve _NT and any additional args from the outer ArrayField
    if len(default_return_type.args) > 2:
        args.extend(default_return_type.args[2:])
    return default_return_type.copy_modified(args=args)
```

- [ ] **Step 5: Validate: custom field "nullable but not optional" check**

The validation at lines 169-176 checks that the get type is Optional when the field is nullable. This is now only hit via `fill_descriptor_types_for_related_field` → `set_descriptor_types_for_field`. It should still work for explicitly-parameterized custom fields like `Field[int, int](null=True)`. Verify with test.

- [ ] **Step 6: Run tests**

Run: `uv run pytest tests/typecheck/fields/ -v --no-header 2>&1 | tail -40`

- [ ] **Step 7: Commit**

```bash
git add mypy_django_plugin/transformers/fields.py
git commit -m "refactor: make plugin no-op for basic fields, preserve related/array handling"
```

---

## Task 6: Update test expectations

**Files:**
- Modify: `tests/typecheck/fields/test_custom_fields.yml`
- Modify: `tests/typecheck/fields/test_nullable.yml`
- Potentially: other test files

After the stub and plugin changes, some test expectations may need updating.

- [ ] **Step 1: Run the full test suite and collect failures**

Run: `uv run pytest tests/typecheck/fields/ -v --no-header 2>&1 | tee /tmp/test_results.txt`

Inspect failures. The main things that might change:
- Custom field patterns with explicit `Field[_ST, _GT]` now need `Field[_ST, _GT, _NT]`
- Revealed types may show the `_NT` parameter
- Error messages may change slightly

- [ ] **Step 2: Update `test_custom_fields.yml`**

In the test models, custom fields using `fields.Field[_ST, _GT]` need to thread `_NT`:

```python
# Old:
class GenericField(fields.Field[_ST, _GT]): ...
class SingleTypeField(fields.Field[T, T]): ...
class CustomValueField(fields.Field[CustomFieldValue | int, CustomFieldValue]): ...

# New:
from typing import Literal
_NT = TypeVar("_NT", Literal[True], Literal[False], default=Literal[False])
class GenericField(fields.Field[_ST, _GT, _NT]): ...
class SingleTypeField(fields.Field[T, T, _NT]): ...
class CustomValueField(fields.Field[CustomFieldValue | int, CustomFieldValue, _NT]): ...
```

Also update usage sites:
```python
# Old:
my_custom_field1 = GenericField[CustomFieldValue | int, CustomFieldValue]()
# New (if 3rd arg needed):
my_custom_field1 = GenericField[CustomFieldValue | int, CustomFieldValue, Literal[False]]()
# Or (if defaults work):
my_custom_field1 = GenericField[CustomFieldValue | int, CustomFieldValue]()
```

**Note:** PEP 696 allows omitting trailing TypeVars that have defaults. So `GenericField[CustomFieldValue | int, CustomFieldValue]` should still work and default `_NT` to `Literal[False]`. Verify this with mypy.

- [ ] **Step 3: Update `test_nullable.yml` if needed**

The `nullable_field_with_strict_optional_true` test case expects this error:
```python
MyModel().text = None  # E: Incompatible types in assignment (expression has type "None", variable has type "str | int | Combinable")
```

With the new overloaded `__set__`, the error message may change. Run the test and update the expected error if needed.

- [ ] **Step 4: Run full test suite**

Run: `uv run pytest tests/ -v --no-header 2>&1 | tail -40`

Fix any remaining failures iteratively.

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "test: update test expectations for PEP 696 field typing"
```

---

## Task 7: Stubtest allowlist updates

**Files:**
- Modify: `scripts/stubtest/allowlist*.txt` (find the exact file with `ls scripts/stubtest/`)

Changing `null: bool = False` → `null: _NT = ...` in stubs causes stubtest failures because at runtime the signature is `null: bool`. This is a known pattern — PR #1900 established the allowlist approach.

- [ ] **Step 1: Find the allowlist file**

Run: `find scripts/ -name 'allowlist*' -o -name 'allow*' | head -20`

Also check if there's a `stubtest` section in `pyproject.toml` or a `Makefile` target.

- [ ] **Step 2: Run stubtest and collect failures**

Run the project's standard stubtest command (likely `uv run python3 -m mypy.stubtest django ...`) and capture all `null` parameter mismatches.

- [ ] **Step 3: Add allowlist entries**

For each field `__init__` that changed `null: bool` to `null: _NT`, add an entry like:
```
# PEP 696: null parameter typed as Literal[True] | Literal[False] for _NT TypeVar
django.db.models.fields.Field.__init__
django.db.models.fields.CharField.__init__
django.db.models.fields.DecimalField.__init__
# ... etc for every field with an overridden __init__
```

Use a regex pattern if the allowlist supports it: `django.db.models.(\w*)Field.__init__`

- [ ] **Step 4: Commit**

```bash
git add scripts/stubtest/
git commit -m "chore: add stubtest allowlist entries for null: _NT parameter"
```

---

## Task 8: Full test suite and cross-type-checker validation

**Files:**
- Potentially any file from Tasks 1-7

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest tests/ -x -v --no-header 2>&1 | tee /tmp/full_test_results.txt`

- [ ] **Step 2: Run stubtest**

Run the project's standard stubtest command and verify all failures are covered by allowlist entries from Task 7.

- [ ] **Step 3: Fix any remaining issues**

Common issues to watch for:
1. **ManyToManyField** — inherits from `RelatedField[Any, Any]` with a separate `Generic[_To, _Through]`. Verify `_NT` threading works with this multiple-inheritance-of-generics pattern.
2. **ArrayField** — the plugin determines the inner type from `base_field`. Verify the 3-arg pattern doesn't break this.
3. **AutoField** — The plugin's `set_descriptor_types_for_field_callback` previously special-cased AutoField with `is_set_nullable=True`. Since this is now a no-op, verify AutoField nullability in `__init__`/`create` contexts still works via the `DjangoContext.get_field_nullability` path.
4. **Custom field validation** — the "nullable but generic get type is not optional" error should still fire for explicit params.

- [ ] **Step 4: Verify with pyright**

Run: `uv run pyright tests/typecheck/ 2>&1 | tail -40`

(If pyright doesn't have a test runner, just verify a sample model file.)

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "fix: resolve remaining issues from PEP 696 field typing migration"
```

---

## Appendix A: Complete TypeVar mapping reference

| Current `_pyi_private_set_type` | New TypeVar default `_ST_*` | Current `_pyi_private_get_type` | New TypeVar default `_GT_*` |
|-|-|-|-|
| **IntegerField**: `float \| int \| str \| Combinable` | `_ST_INT` | `int` | `_GT_INT` |
| **FloatField**: `float \| int \| str \| Combinable` | `_ST_FLOAT` | `float` | `_GT_FLOAT` |
| **DecimalField**: `str \| float \| Decimal \| Combinable` | `_ST_DECIMAL` | `Decimal` | `_GT_DECIMAL` |
| **CharField**: `str \| int \| Combinable` | `_ST_CHAR` | `str` | `_GT_CHAR` |
| **EmailField**: `str \| Combinable` | `_ST_EMAIL` (inherits `_GT_CHAR`) | (inherits `str`) | (inherits) |
| **TextField**: `str \| Combinable` | `_ST_TEXT` | `str` | `_GT_TEXT` |
| **BooleanField**: `bool \| Combinable` | `_ST_BOOL` | `bool` | `_GT_BOOL` |
| **NullBooleanField**: `bool \| Combinable \| None` | `_ST_NBOOL` | `bool \| None` | `_GT_NBOOL` |
| **IPAddressField**: `str \| Combinable` | `_ST_IP` | `str` | `_GT_IP` |
| **GenericIPAddressField**: `str \| int \| Callable \| Combinable` | `_ST_GENIP` | `str` | (shares `_GT_IP`) |
| **DateField**: `str \| date \| Combinable` | `_ST_DATE` | `date` | `_GT_DATE` |
| **TimeField**: `str \| time \| datetime \| Combinable` | `_ST_TIME` | `time` | `_GT_TIME` |
| **DateTimeField**: `str \| datetime \| date \| Combinable` | `_ST_DATETIME` | `datetime` | `_GT_DATETIME` |
| **UUIDField**: `str \| uuid.UUID` | `_ST_UUID` | `uuid.UUID` | `_GT_UUID` |
| **BinaryField**: (none) | (inherits `_ST`) | `bytes \| memoryview` | `_GT_BINARY` |
| **DurationField**: (none) | (inherits `_ST`) | `timedelta` | `_GT_DURATION` |
| **AutoField**: `Combinable \| int \| str` | `_ST_AUTO` | `int` | `_GT_AUTO` |
| **ArrayField**: `Sequence[Any] \| Combinable` | `_ST_ARRAY` | `list[Any]` | `_GT_ARRAY` |
| **ForeignKey**: `Any \| Combinable` | (inherits `_ST`, default `Any`) | `Any` | (inherits `_GT`, default `_ST`) |
| **OneToOneField**: `Any \| Combinable` | (inherits from FK) | `Any` | (inherits from FK) |
| **GenericForeignKey**: `Any \| Combinable` | (remove, has own `__set__`) | `Any` | (remove, has own `__get__`) |
| **PointField**: `Point \| Combinable` | `_ST_POINT` | `Point` | `_GT_POINT` |
| (etc. for all 7 geometry fields) | | | |

## Appendix B: Known risks and mitigations

1. **Custom fields breaking** — Users with `class MyField(Field[_ST, _GT])` need to add `_NT` or drop explicit params. Mitigation: PEP 696 defaults mean `Field[_ST, _GT]` still works (`_NT` defaults to `Literal[False]`). But if the user's `_ST`/`_GT` don't have their own defaults, accessing `.field_name` on a model will yield the TypeVar, not the default. Document this in migration guide.

2. **`null` parameter no longer accepts `bool` variables** — `null: _NT = ...` is constrained to `Literal[True]` and `Literal[False]`. Passing `null=some_bool_var` won't work. Mitigation: This is always a literal in practice for model definitions. The plugin handles dynamic contexts.

3. **Plugin TypeVar default reading** — `TypeVarType.default` might not be populated in all mypy code paths. Mitigation: The `has_default` guard + fallback to `AnyType`.

4. **Custom fields with `*args, **kwargs` passthrough** — If a third-party field overrides `__init__` with `(*args, **kwargs)`, the `null` parameter disappears into `**kwargs` and `_NT` can't be inferred. This affects `django-money`, `django-phonenumber-field`, etc. Mitigation: Users can manually parameterize `MyField[ST, GT, Literal[True]]`. This is a pre-existing limitation (the current plugin approach also doesn't handle `**kwargs` passthrough).

5. **Stubtest failures** — `null: _NT` vs runtime `null: bool` will fail stubtest. Mitigation: Allowlist entries (established pattern from PR #1900).

6. **mypy minimum version bump** — Requires mypy >= 1.16 for inherited descriptor overloads. This drops support for mypy 1.13-1.15. Mitigation: Users on older mypy versions can pin `django-stubs` to the pre-change version.

7. **AutoField special nullability** — AutoField has no `null=True` in code, but the plugin makes it nullable in `__init__`/`create` contexts (auto-increment fields can be omitted). With the basic-fields no-op change (Task 5), this is handled entirely by `DjangoContext.get_field_nullability` + `get_field_set_type`, which still works. Verify this explicitly.

8. **`AbstractBaseSession.pk`** — This is a CharField (session_key is PK), not an AutoField. Don't assume `pk` is always `int`.
