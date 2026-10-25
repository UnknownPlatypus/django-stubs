# django-types merged PRs: cherry-pick triage for django-stubs

All 284 merged PRs of [sbdchd/django-types](https://github.com/sbdchd/django-types/pulls?q=is%3Amerged), compared against django-stubs `field-typevar-any-defaults`.
229 touch stubs and were reviewed hunk by hunk; 55 only touch releases/CI/docs/psycopg2 (listed at the end).

Verdicts: ✅ yes 7, 🟡 partial 26, ❌ no 6, ➖ already 163, ➖ n/a 27
(5 of the yes/partial ones are deferred until the manager/queryset refactor.)

Porting progress (2026-10-25): ✅ 26 merged, 🟢 1 open (#3738, review comments answered), ⏸ 6 deferred (5 manager/queryset pending #2776, #316 pending the field access rework). Nothing left to open outside the deferred ones.

Follow-ups found during triage (2026-10-25), pushed but not opened: `assert-type-existing-stubs` (Proposed tests for the ➖ already rows; skipped #407, #268 and #64 as duplicate coverage). The #350 (`Signal.send`, #841) and #337 (`Q(...) | Exists(...)`) fixes were dropped.

- **yes**: django-stubs lacks it and it matches runtime Django.
- **partial**: only some hunks are worth porting (see note).
- **already**: django-stubs has it or something equivalent/better.
- **n/a**: django-types-specific design (plugin-less workarounds), tooling or formatting.
- **no**: wrong vs runtime Django or would regress django-stubs.

## To port

Sorted from easiest to heaviest. Effort: **XS** one or two lines, **S** a few attributes/params, **M** several hunks plus a test, **L** multi-file or version-split or plugin interaction.

| Status | Effort | PR | Title | Cherry-pickable | What to port | Fixes django-stubs issue | Test to add |
|---|---|---|---|---|---|---|---|
| ✅ merged [#3718](https://github.com/typeddjango/django-stubs/pull/3718) | XS | [#108](https://github.com/sbdchd/django-types/pull/108) | Update dependencies and fix typing issues | 🟡 partial | Port only source_is_geography -> bool: runtime returns geo_field.geography and srid == 4326, stub still Any (contrib/gis/db/models/functions.pyi:116). output_field (:114-115), ImmutableList.__new__ Self (utils/datastructures.pyi:112) already there. | - | - |
| ✅ merged [#3719](https://github.com/typeddjango/django-stubs/pull/3719) | XS | [#170](https://github.com/sbdchd/django-types/pull/170) | Add typing to Graph and Node | 🟡 partial | node_map/nodes already typed (graph.pyi:32-33, nodes even allows None). Port only Node.children/parents set[Any] -> set[Node] (graph.pyi:10-11); runtime add_child/add_parent only store Nodes. | - | - |
| ✅ merged [#3720](https://github.com/typeddjango/django-stubs/pull/3720) | XS | [#338](https://github.com/sbdchd/django-types/pull/338) | fix: use sequence instead of list in send_mass_mail | 🟡 partial | Outer is already Iterable (core/mail/__init__.pyi:40). The inner recipient `list[str]` should become Sequence[str], matching EmailMessage(to: Sequence[str]), which receives it at runtime. | - | - |
| ✅ merged [#3721](https://github.com/typeddjango/django-stubs/pull/3721) | XS | [#263](https://github.com/sbdchd/django-types/pull/263) | Add `db_default` arg to `Field` constructors | 🟡 partial | Params exist (fields/__init__.pyi:182). Port the attribute: :144 types it type[NOT_PROVIDED] \| Expression, but Django 5.2/6.1 store the raw value and wrap it only in _db_default_expression; widen with \| Any. | - | - |
| ✅ merged [#3722](https://github.com/typeddjango/django-stubs/pull/3722) | XS | [#65](https://github.com/sbdchd/django-types/pull/65) | Fields typing improvements | 🟡 partial | Port only FilePathField.path: Any -> str \| Callable[..., str] (fields/__init__.pyi:630, matches runtime self.path). Rest: overloads (see #3317), wrong (TextField(CharField), _Choice label str, DecimalField auto_now, IPv4Address set type) or already. |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| ✅ merged [#3723](https://github.com/typeddjango/django-stubs/pull/3723) | XS | [#419](https://github.com/sbdchd/django-types/pull/419) | Widen setup_databases aliases and ListFilter.choices | 🟡 partial | Port aliases: Collection[str] \| None (test/utils.pyi:162 set[str], :172 Mapping[str, Any]); runtime only does `alias in aliases`, runner passes a dict. ListFilter.choices already Iterator[Mapping[str, object]] (filters.pyi:33); #2508 needs subclass overrides changed, not this. | - | - |
| ✅ merged [#3724](https://github.com/typeddjango/django-stubs/pull/3724) | XS | [#378](https://github.com/sbdchd/django-types/pull/378) | sync sitemaps from django-stubs | 🟡 partial | Port only Mapping (keep Any, not _T) in django-stubs/contrib/sitemaps/views.pyi:20,27: invariant dict rejects dict[str, MySitemap] on all 4 checkers; runtime only reads it. Rest: django-stubs equal/better (FlatPageSitemap[FlatPage]). | - | - |
| ✅ merged [#3725](https://github.com/typeddjango/django-stubs/pull/3725) | S | [#413](https://github.com/sbdchd/django-types/pull/413) | declare the public members BaseDatabaseWrapper was missing | 🟡 partial | Six already in django-stubs/db/backends/base/base.pyi:66-112. Port the missing instance attributes rollback_exc: Exception \| None, health_check_enabled: bool, health_check_done: bool (set in runtime __init__) near :53-56. | - | - |
| ✅ merged [#3726](https://github.com/typeddjango/django-stubs/pull/3726) | S | [#348](https://github.com/sbdchd/django-types/pull/348) | Add types for `GeneratedField` | 🟡 partial | GeneratedField exists (fields/generated.pyi:15) but lacks the expression attribute (and db_persist) set in runtime __init__; pyright errors on field.expression. Port those. Overload-based get typing is n/a. | - | - |
| ✅ merged [#3728](https://github.com/typeddjango/django-stubs/pull/3728) | S | [#325](https://github.com/sbdchd/django-types/pull/325) | fix: Fix invalid type for form in `construct_change_message` | ✅ yes | options.pyi:281 and utils.pyi:116 take forms.Form, so passing ModelForm (BaseForm, not Form) fails on all 4 checkers. Use BaseForm. Also accept formsets=None, which Django passes (options.py:2307, auth/admin.py:180). | - | - |
| ✅ merged [#3729](https://github.com/typeddjango/django-stubs/pull/3729) | S | [#376](https://github.com/sbdchd/django-types/pull/376) | sync StrOrPromise with django-stubs | 🟡 partial | Mostly already present. Port: DecimalValidator.messages dict[str, _StrOrPromise] (lazy at runtime; core/validators.pyi:138), assertRedirects expected_url _StrOrPromise (str()-coerced; test/testcases.pyi:76), optionally URLValidator schemes Collection[str] (:57,60). Test only covers existing slugify TypeVar. | - | add: tests/assert_type/utils/test_text.py |
| ✅ merged [#3730](https://github.com/typeddjango/django-stubs/pull/3730) | S | [#360](https://github.com/sbdchd/django-types/pull/360) | Allow `Q` objects to be passed to `django.db.models.Index` | ✅ yes | Runtime accepts it: Index(Q(author__isnull=False), name=...) emits (("author" IS NOT NULL)) on Django 6.1. Widen db/models/indexes.pyi:27 (and expressions attr :23) plus the postgres index subclasses (contrib/postgres/indexes.pyi:27-110). | - | - |
| ✅ merged [#3731](https://github.com/typeddjango/django-stubs/pull/3731) | S | [#54](https://github.com/sbdchd/django-types/pull/54) | Improve objects inside Model | 🟡 partial | Port only `Options.model: type[_M]` (django-stubs/db/models/options.pyi:83, now type[Model]; all 4 checkers give type[Model]). ModelBase.objects n/a (base.pyi:55); _meta/default_manager already; proxy_for_model/concrete_model are parents, not _M; ContentTypeManager->BaseManager wrong. | - | add: tests/assert_type/db/models/test_base.py |
| ✅ merged [#3732](https://github.com/typeddjango/django-stubs/pull/3732) | S | [#210](https://github.com/sbdchd/django-types/pull/210) | Improve `django.template` | 🟡 partial | Port only select_template's return (template/loader.pyi:11 is Any), typed _EngineTemplate like get_template, not base.Template. get_template/get_app_template_dirs already better. __iter__ -> BaseEngine is wrong: runtime iterates aliases (str). | - | add: tests/assert_type/template/test_loader.py |
| ✅ merged [#3734](https://github.com/typeddjango/django-stubs/pull/3734) | S | [#397](https://github.com/sbdchd/django-types/pull/397) | Improve `django-stubs/test/client.pyi` | 🟡 partial | Port check_exception -> None: client.pyi:262 says NoReturn but runtime only raises if exc_info is set and raise_request_exception, so mypy marks code after it unreachable (verified). Optional: conditional_content_removal generic (client.pyi:50). Rest already; query_params: str is wrong. | - | add: tests/assert_type/test/test_client.py |
| ✅ merged [#3733](https://github.com/typeddjango/django-stubs/pull/3733) | S | [#213](https://github.com/sbdchd/django-types/pull/213) | django/test/utils.py polish | 🟡 partial | Only missing piece: decorate_class keeps the class type (utils.pyi:64 returns _TestClass, override_settings utils.pyi:75 returns bare type). Low value, direct calls are rare. __call__ (utils.pyi:66), __enter__ Self, tag, setup_databases already better; generic ContextList not worth it. | - | add: tests/assert_type/test/test_utils.py |
| ✅ merged [#3735](https://github.com/typeddjango/django-stubs/pull/3735) | M | [#271](https://github.com/sbdchd/django-types/pull/271) | forms/formsets: Improve types | 🟡 partial | Generic BaseFormSet and formset_factory already exist (forms/formsets.pyi:30-129). Port BaseFormSet.errors -> list[ErrorDict] (formsets.pyi:100 says list[ErrorList]; runtime appends form.errors). Optionally deletion/ordering_widget: type[Widget] (formsets.pyi:50-51). | - | add: tests/assert_type/forms/test_formsets.py |
| ✅ merged [#3736](https://github.com/typeddjango/django-stubs/pull/3736) | M | [#246](https://github.com/sbdchd/django-types/pull/246) | Improvements to `django.contrib.auth` | 🟡 partial | Port only AnonymousUser save/delete/set_password/check_password -> Never (always raise NotImplementedError) and (a)get_group_permissions -> set[str] (contrib/auth/models.pyi:138-141,148-149). AbstractUser returns would break custom AbstractBaseUser models; rest already. | - | add: tests/assert_type/contrib/auth/test_user_flags/models.py |
| ✅ merged [#3737](https://github.com/typeddjango/django-stubs/pull/3737) | M | [#208](https://github.com/sbdchd/django-types/pull/208) | Improve `django.http` types | 🟡 partial | Port only get_signed_cookie default TypeVar, as overloads: no default -> str, default: _Z -> str \| _Z (request.pyi:83 returns str \| None). Optional: to_wsgi_names/to_asgi_names Mapping[str, _V] -> dict[str, _V] (request.pyi:43). Rest already; encoding -> str is wrong (_encoding defaults None). | - | add: tests/assert_type/http/test_request.py |
| 🟢 open, comments answered [#3738](https://github.com/typeddjango/django-stubs/pull/3738) | M | [#189](https://github.com/sbdchd/django-types/pull/189) | Add TransactionTestCase.assertQuerySetEqual | ✅ yes | testcases.pyi:201 types transform as Callable[[Model], Any]: mypy rejects lambda u: u.username, (Blog) -> str functions and transform=tuple on values_list (verified). Port as qs: Iterable[_T], transform: Callable[[_T], Any] \| None, which also covers PR 197. | - | add: tests/assert_type/test/test_testcase.py |
| ✅ merged [#3739](https://github.com/typeddjango/django-stubs/pull/3739) | M | [#159](https://github.com/sbdchd/django-types/pull/159) | feat: support for Django 4.2 | 🟡 partial | Port only staff_member_required: the first overload's `view_func: _C = ...` default makes `staff_member_required(login_url=...)` infer Never/Unknown (contrib/admin/views/decorators.pyi:10). Drop it and mirror login_required's _VIEW / Callable[[_VIEW], _VIEW]. Other hunks: already or n/a. | - | add: tests/assert_type/contrib/admin/views/test_decorators.py |
| ✅ merged [#3741](https://github.com/typeddjango/django-stubs/pull/3741) | M | [#362](https://github.com/sbdchd/django-types/pull/362) | Improve `django.core.management` types | 🟡 partial | Port: CommandParser.error -> NoReturn (base.pyi:26, always raises), OutputWrapper not subclassing TextIOBase (base.pyi:38, true since Django 5.2), __getattr__ -> Any, handle_app_config(AppConfig), LabelCommand.missing_args_message: str. Optional: call_command -> str \| None. | - | add: tests/assert_type/core/management/test_base.py |
| ✅ merged [#3742](https://github.com/typeddjango/django-stubs/pull/3742) | M | [#257](https://github.com/sbdchd/django-types/pull/257) | contrib/admin/options: improve types | 🟡 partial | Port only save_form(..., change: bool) -> _ModelT (options.pyi:291, now Any) and action_form: ClassVar[type[ActionForm]] (:203). Rest is already in place or wrong at runtime: Mapping context (it calls .update), changeform_view -> TemplateResponse, formsets: BaseModelFormSet. | - | add: tests/assert_type/contrib/admin/test_options.py |
| ✅ merged [#3743](https://github.com/typeddjango/django-stubs/pull/3743) | L | [#10](https://github.com/sbdchd/django-types/pull/10) | add(django): type csrf and vary decorators | ✅ yes | csrf.pyi:7,11,15 are module-level Callable[[_F], _F] vars: pyright infers Any, ty errors (Expected TypeVar), verified. Same fix needed for http.pyi:13-15 require_*, conditional_page, gzip.pyi:8. vary already. |  (in flight: [#2164](https://github.com/typeddjango/django-stubs/pull/2164)) | add: tests/assert_type/views/test_decorators.py |
| ✅ merged [#3756](https://github.com/typeddjango/django-stubs/pull/3756) | L | [#408](https://github.com/sbdchd/django-types/pull/408) | let every field's choices= accept what Field.choices already does | 🟡 partial | fields/__init__ already uses _ChoicesInput. FileField (files.pyi:84), related fields (related.pyi:72,128,217,290,356), ArrayField (array.pyi:55) and GIS fields still take _Choices \| None, so pyright rejects mappings, Choices classes and callables. Widen them. Per-field Choices precision is n/a. | - | - |
| ✅ merged [#3755](https://github.com/typeddjango/django-stubs/pull/3755) | L | [#258](https://github.com/sbdchd/django-types/pull/258) | Improve types around template rendering | 🟡 partial | Port: forms/renderers.pyi:19,23 get_template Any -> _EngineTemplate, backend-specific overrides, fix :36 TemplatesSetting (base.Template\|None), loader.pyi:11 select_template, django Template.render -> SafeString. Skip Mapping contexts (make_context needs dict), Div renderers (removed 5.0). | - | add: tests/assert_type/forms/test_renderers.py |
| ⏸ deferred (field access rework) | L | [#316](https://github.com/sbdchd/django-types/pull/316) | Add django-stub for Composite Primary Key  | 🟡 partial | composite.pyi exists, but CompositePrimaryKey(Field[Any, Any]) (fields/composite.pyi:24) reads Any. Port typed get/set, fixing the PR: CompositeAttribute.__get__ always returns a tuple. Set _pyi_private_* too, for the plugin's pk alias. | - | add: tests/assert_type/db/models/fields/test_composite_pk/models.py |
| ✅ merged [#3758](https://github.com/typeddjango/django-stubs/pull/3758) | L | [#414](https://github.com/sbdchd/django-types/pull/414) | type admin action callables as returning HttpResponseBase \| None | ✅ yes | Adapt to version split: 5.2 branch options.pyi:262,266 use Callable[..., str] and \|None values. 6.1 branch :249 has Action \| None (runtime never stores None), and Action.func :62 rejects subclass methods. Use _ActionCallable[Any, Any]. | - | add: tests/assert_type/contrib/admin/test_options.py |

## Deferred: manager/queryset

Pending the manager-generic-on-queryset refactor (see draft [#2776](https://github.com/typeddjango/django-stubs/pull/2776)). Listed in dependency order.

| Status | PR | Title | Cherry-pickable | What to port | Fixes django-stubs issue | Test to add |
|---|---|---|---|---|---|---|
| ⏸ deferred | [#416](https://github.com/sbdchd/django-types/pull/416) | type manager chain calls as returning the manager's queryset | ✅ yes | manager.pyi:46-47,146-186 return QuerySet[_T], so pyright/ty/pyrefly lose custom querysets (verified). Needs plugin follow-up. Draft #2776 does this but keeps union/intersection/difference/reverse as QuerySet[_T]; runtime proxies all through get_queryset(). | [#863](https://github.com/typeddjango/django-stubs/issues/863) (in flight: [#2776](https://github.com/typeddjango/django-stubs/pull/2776)) | add: tests/assert_type/db/models/test_managers.py |
| ⏸ deferred | [#421](https://github.com/sbdchd/django-types/pull/421) | fix(typing): preserve queryset type in as_manager | ✅ yes | query.pyi:93 returns Manager[_Model], so for pyright/ty/pyrefly `MyQS.as_manager().filter()` is QuerySet[M] (verified). The mypy plugin already handles this. Depends on #416's _QS param; #2776 includes this exact change. |  (in flight: [#2776](https://github.com/typeddjango/django-stubs/pull/2776)) | add: tests/assert_type/db/models/test_managers.py |
| ⏸ deferred | [#423](https://github.com/sbdchd/django-types/pull/423) | type AbstractBaseUser.is_active, Manager._queryset_class and Options.fields to match runtime | 🟡 partial | Port the missing `_queryset_class: type[QuerySet[Any, Any]]` on Manager; #2776's type[_QS] would reject generic subclasses. Options.fields already (options.pyi:113). Reject is_active: base_user.pyi:26's union lets models override it with BooleanField. | - | - |
| ⏸ deferred | [#412](https://github.com/sbdchd/django-types/pull/412) | Fix queryset variance and enum choices compatibility with ty | 🟡 partial | Port only `__class_getitem__(cls, *args: Any, **kwargs: Any) -> type[Self]`. Runtime returns cls, while query.pyi:107 says `-> Self`; manager.pyi:33 already does this. The ty ignores (stubs aren't ty-checked) and _I/_C field TypeVars don't apply. | - | - |
| ⏸ deferred | [#190](https://github.com/sbdchd/django-types/pull/190) | Make managers in `django.contrib` generic | 🟡 partial | Port generic Log/Permission/Group/SiteManager with `objects: ClassVar[XManager[Self]]` (contrib/auth/models.pyi:33-52, sites/models.pyi:8-14, admin/models.pyi:16-46): mypy gives Group for ProxyGroup.objects.get(). Also Session overrides (sessions/models.pyi:7). Rest already. #2590/#2214 do Session.objects only. |  (in flight: [#2590](https://github.com/typeddjango/django-stubs/pull/2590)) | add: tests/assert_type/contrib/auth/test_models.py |

## All reviewed PRs

| PR | Title | Cherry-pickable | Note | Fixes django-stubs issue | Test to add |
|---|---|---|---|---|---|
| [#426](https://github.com/sbdchd/django-types/pull/426) | Type prefetch_related lookups and infer Prefetch models | ➖ already | Already overloaded on QuerySet and Manager (django-stubs/db/models/query.pyi:222-225, manager.pyi:162-165). Prefetch is generic over lookup/queryset/to_attr with a nullable queryset (query.pyi:304-311). Only mypy yml tests cover it. | - | add: tests/assert_type/db/models/test_query.py |
| [#425](https://github.com/sbdchd/django-types/pull/425) | Stop modelling managers as QuerySet subclasses | ➖ already | django-types follows django-stubs here: BaseManager is Generic[_T] (manager.pyi:24) and Manager redeclares the proxied methods (manager.pyi:59-186). The _QS parts are #416/#2776; Manager.extra->_QS conflicts with the deliberate QuerySet[Any]. | - | add: tests/assert_type/db/models/test_managers.py |
| [#423](https://github.com/sbdchd/django-types/pull/423) | type AbstractBaseUser.is_active, Manager._queryset_class and Options.fields to match runtime | 🟡 partial ⏸ deferred | Port the missing `_queryset_class: type[QuerySet[Any, Any]]` on Manager; #2776's type[_QS] would reject generic subclasses. Options.fields already (options.pyi:113). Reject is_active: base_user.pyi:26's union lets models override it with BooleanField. | - | - |
| [#422](https://github.com/sbdchd/django-types/pull/422) | Fix remote_field relation types | ➖ already | Field.remote_field: ForeignObjectRel \| None (fields/__init__.pyi:124); RelatedField/ForeignObject ForeignObjectRel, ForeignKey ManyToOneRel, OneToOneField OneToOneRel, ManyToManyField ManyToManyRel (related.pyi:48,98,186,260,325). | - | - |
| [#421](https://github.com/sbdchd/django-types/pull/421) | fix(typing): preserve queryset type in as_manager | ✅ yes ⏸ deferred | query.pyi:93 returns Manager[_Model], so for pyright/ty/pyrefly `MyQS.as_manager().filter()` is QuerySet[M] (verified). The mypy plugin already handles this. Depends on #416's _QS param; #2776 includes this exact change. |  (in flight: [#2776](https://github.com/typeddjango/django-stubs/pull/2776)) | add: tests/assert_type/db/models/test_managers.py |
| [#420](https://github.com/sbdchd/django-types/pull/420) | Type BaseDatabaseWrapper.execute_wrapper and constraint_checks_disabled as context managers | ➖ already | django-stubs/db/backends/base/base.pyi:102,125 already return AbstractContextManager[None], with a typed _ExecuteWrapper callable (:25). Untested; snippet verified on mypy, pyright, ty. | - | add: tests/assert_type/db/test_connection.py |
| [#419](https://github.com/sbdchd/django-types/pull/419) | Widen setup_databases aliases and ListFilter.choices | 🟡 partial | Port aliases: Collection[str] \| None (test/utils.pyi:162 set[str], :172 Mapping[str, Any]); runtime only does `alias in aliases`, runner passes a dict. ListFilter.choices already Iterator[Mapping[str, object]] (filters.pyi:33); #2508 needs subclass overrides changed, not this. | - | - |
| [#418](https://github.com/sbdchd/django-types/pull/418) | type checks.register and the model formset factories | ➖ already | core/checks/registry.pyi:26-67 has register overloads with _ProcessedCheckCallable and registry: CheckRegistry; forms/models.pyi formset params are already parametrized (BaseModelFormSet[Any, Any]); binding them to the factory TypeVars would conflict with form=. | - | existing: tests/assert_type/core/test_checks.py |
| [#417](https://github.com/sbdchd/django-types/pull/417) | export the _User alias django-stubs defines | ➖ already | django-stubs defines _User: TypeAlias = AbstractBaseUser at contrib/auth/models.pyi:19; this PR only mirrors it in django-types. | - | - |
| [#416](https://github.com/sbdchd/django-types/pull/416) | type manager chain calls as returning the manager's queryset | ✅ yes ⏸ deferred | manager.pyi:46-47,146-186 return QuerySet[_T], so pyright/ty/pyrefly lose custom querysets (verified). Needs plugin follow-up. Draft #2776 does this but keeps union/intersection/difference/reverse as QuerySet[_T]; runtime proxies all through get_queryset(). | [#863](https://github.com/typeddjango/django-stubs/issues/863) (in flight: [#2776](https://github.com/typeddjango/django-stubs/pull/2776)) | add: tests/assert_type/db/models/test_managers.py |
| [#415](https://github.com/sbdchd/django-types/pull/415) | declare Model.objects on ModelBase so models can narrow their manager | ➖ already | django-stubs already falls back via ModelBase.__getattr__(cls, 'objects') -> Manager[_Self] (django-stubs/db/models/base.pyi:51-55, PR #3559). Instance access is already rejected. | - | existing: tests/assert_type/db/models/test_manager_access/models.py |
| [#414](https://github.com/sbdchd/django-types/pull/414) | type admin action callables as returning HttpResponseBase \| None | ✅ yes | Adapt to version split: 5.2 branch options.pyi:262,266 use Callable[..., str] and \|None values. 6.1 branch :249 has Action \| None (runtime never stores None), and Action.func :62 rejects subclass methods. Use _ActionCallable[Any, Any]. | - | add: tests/assert_type/contrib/admin/test_options.py |
| [#413](https://github.com/sbdchd/django-types/pull/413) | declare the public members BaseDatabaseWrapper was missing | 🟡 partial | Six already in django-stubs/db/backends/base/base.pyi:66-112. Port the missing instance attributes rollback_exc: Exception \| None, health_check_enabled: bool, health_check_done: bool (set in runtime __init__) near :53-56. | - | - |
| [#412](https://github.com/sbdchd/django-types/pull/412) | Fix queryset variance and enum choices compatibility with ty | 🟡 partial ⏸ deferred | Port only `__class_getitem__(cls, *args: Any, **kwargs: Any) -> type[Self]`. Runtime returns cls, while query.pyi:107 says `-> Self`; manager.pyi:33 already does this. The ty ignores (stubs aren't ty-checked) and _I/_C field TypeVars don't apply. | - | - |
| [#411](https://github.com/sbdchd/django-types/pull/411) | Sync django.conf and django.urls stubs | ➖ already | Verbatim copy: every added line exists in current django-stubs (urls/resolvers.pyi:130 differs only in union order). Only diff is `from . import global_settings as global_settings` vs plain import in conf/__init__.pyi:7, no practical effect. | - | existing: tests/assert_type/urls/test_conf.py |
| [#410](https://github.com/sbdchd/django-types/pull/410) | Expose Django settings and storage alias constants | ➖ already | conf/__init__.pyi:9-11 already declares all three as Literal. | - | - |
| [#409](https://github.com/sbdchd/django-types/pull/409) | django.contrib.auth.decorators: sync with django-stubs | ➖ already | Byte-identical to django-stubs/contrib/auth/decorators.pyi. | - | existing: tests/typecheck/contrib/auth/test_decorators.yml |
| [#408](https://github.com/sbdchd/django-types/pull/408) | let every field's choices= accept what Field.choices already does | 🟡 partial | fields/__init__ already uses _ChoicesInput. FileField (files.pyi:84), related fields (related.pyi:72,128,217,290,356), ArrayField (array.pyi:55) and GIS fields still take _Choices \| None, so pyright rejects mappings, Choices classes and callables. Widen them. Per-field Choices precision is n/a. | - | - |
| [#407](https://github.com/sbdchd/django-types/pull/407) | fix field descriptor types that force casts or dead guards | ➖ already | Field TypeVars default to Any (fields/__init__.pyi:53-55, related.pyi:37-39, json.pyi:18-20); FileField is Field[Any, Any] (files.pyi:58); max_length: int \| None (:132). No plugin-less assert_type covers lazy FKs. | - | add: tests/assert_type/db/models/fields/test_lazy_reference/models.py |
| [#406](https://github.com/sbdchd/django-types/pull/406) | correct signatures that misdescribe Django's own API | ➖ already | Every hunk already matches or exceeds: operations.pyi:74, loader.pyi:20, main.pyi:75, base.pyi:85, resolvers.pyi:132, client.pyi:178 (generic returns _T, response for Client), query_params Mapping, StreamingHttpResponse Iterable[object], base_session.pyi:11-27, questioner.pyi:37. | - | existing: tests/assert_type/test/test_client.py |
| [#405](https://github.com/sbdchd/django-types/pull/405) | add symbols Django exports but the stubs omit | ➖ already | All present: test/__init__.pyi:1-2, http/__init__.pyi:13, testcases.pyi:220, core/files/storage/__init__.pyi:21, utils/http.pyi:40, http/response.pyi:52; contrib/admin/sites.pyi:55 get_model_admin is even generic (ModelAdmin[_ModelT]). | - | add: tests/assert_type/contrib/admin/test_sites.py |
| [#404](https://github.com/sbdchd/django-types/pull/404) | django.utils.timezone: sync with django-stubs | ➖ already | timezone/dateformat/tz identical to django-stubs; django-stubs/tasks/base.pyi already has the takes_context Concatenate overloads plus **kwargs and frozen/slots dataclass. | - | existing: tests/assert_type/tasks/test_tasks.py |
| [#398](https://github.com/sbdchd/django-types/pull/398) | sync contrib.gis.geoip2 from django-stubs | ➖ already | django-stubs/contrib/gis/geoip2.pyi identical; django-stubs/forms/fields.pyi already uses Iterable[_ValidatorCallable] everywhere (e.g. :122). | - | - |
| [#397](https://github.com/sbdchd/django-types/pull/397) | Improve `django-stubs/test/client.pyi` | 🟡 partial | Port check_exception -> None: client.pyi:262 says NoReturn but runtime only raises if exc_info is set and raise_request_exception, so mypy marks code after it unreachable (verified). Optional: conditional_content_removal generic (client.pyi:50). Rest already; query_params: str is wrong. | - | add: tests/assert_type/test/test_client.py |
| [#396](https://github.com/sbdchd/django-types/pull/396) | Fix/model save keyword only args | ➖ already | Already keyword-only (django-stubs/db/models/base.pyi:98-113). | - | - |
| [#394](https://github.com/sbdchd/django-types/pull/394) | sync core.cache with django-stubs | ➖ already | Verbatim copies; django-stubs/core/cache/backends/base.pyi parametrises Callable, utils/connection.pyi:24 has settings_name: str \| None (matches runtime BaseConnectionHandler.settings_name = None). | - | - |
| [#393](https://github.com/sbdchd/django-types/pull/393) | add django.tasks, django.utils.csp, update models.constraints | ➖ already | All copied from django-stubs; current django-stubs is ahead: tasks/base.pyi takes_context overloads + frozen dataclass, ParamSpec'd backends, utils/csp.pyi nonce_attr, constraints.pyi UniqueConstraint name: str required. | - | existing: tests/assert_type/tasks/test_tasks.py |
| [#392](https://github.com/sbdchd/django-types/pull/392) | sync forms from django stubs | ➖ already | Synced lines all present (often improved). django-types-only remnants are plugin-less design (generic AuthenticationForm/PasswordResetForm/LoginView[_UserType] vs plugin-resolved _User, contrib/auth/forms.pyi:94) or wrong for 6.1 (empty_label '---------', changed_data cached_property). | - | existing: tests/assert_type/forms/modelformsets/models.py |
| [#391](https://github.com/sbdchd/django-types/pull/391) | sync core/exceptions and test/runner | ➖ already | Verbatim copies; django-stubs/core/exceptions.pyi adds FieldFetchBlocked, test/runner.pyi identical, test/utils.pyi:96 already dropped the _SupportsContains base django-types still carries. | - | - |
| [#390](https://github.com/sbdchd/django-types/pull/390) | update return type on AdminSite.get_urls | ➖ already | django-stubs/contrib/admin/sites.pyi:63 already returns list[URLResolver \| URLPattern] (urls property :65 too). | - | - |
| [#388](https://github.com/sbdchd/django-types/pull/388) | add db_default to JSONField | ➖ already | JSONField.__init__ forwards **kwargs: Any (django-stubs/db/models/fields/json.pyi:31) to Field.__init__, which has db_default (fields/__init__.pyi:182). | - | - |
| [#386](https://github.com/sbdchd/django-types/pull/386) | match django re-imports in django.db.models | ➖ already | Every added re-export (AnyValue, DEFERRED, WindowFrameExclusion, CommaSeparatedIntegerField, Empty, NullBooleanField, JSONArray, MD5, Random, ExtractIsoWeekDay, AND/OR/XOR) exists; runtime __all__ equals stub __all__ for db, db.models, functions, sql (db/models/__init__.pyi:6-82). Rest is verbatim django-stubs. | - | - |
| [#385](https://github.com/sbdchd/django-types/pull/385) | drop ValuesQuerySet | ➖ already | This brings django-types onto django-stubs' existing design: QuerySet[_Model, _Row] (django-stubs/db/models/query.pyi:80), _ExecuteQuery/_ExecuteParameters (db/backends/utils.pyi:19,36), Mapping-typed related-manager defaults. The psycopg2 removal doesn't apply here. | - | - |
| [#383](https://github.com/sbdchd/django-types/pull/383) | bump mypy to v2 | ➖ already | The semantic hunks copy django-stubs (contrib/admin/decorators.pyi, utils/decorators.pyi, db/models/__init__.pyi:118 __all__). The rest is mypy/pyright config, lockfile and ignore-comment churn. | - | - |
| [#380](https://github.com/sbdchd/django-types/pull/380) | sync django.core.validators with django-stubs | ➖ already | Verbatim django-stubs copy; django-stubs/core/validators.pyi and django-stubs/utils/deconstruct.pyi identical except File[Any] parametrisation. | - | - |
| [#378](https://github.com/sbdchd/django-types/pull/378) | sync sitemaps from django-stubs | 🟡 partial | Port only Mapping (keep Any, not _T) in django-stubs/contrib/sitemaps/views.pyi:20,27: invariant dict rejects dict[str, MySitemap] on all 4 checkers; runtime only reads it. Rest: django-stubs equal/better (FlatPageSitemap[FlatPage]). | - | - |
| [#377](https://github.com/sbdchd/django-types/pull/377) | Restore ruff | ➖ already | All present: __enter__ -> Self (db/backends/utils.pyi:47, db/backends/base/schema.pyi:66, template/context.pyi:20, utils/archive.pyi:14), measure.pyi:23-30, core/mail/backends/base.pyi:20-25, forms/boundfield.pyi:29, utils/datastructures.pyi:72, typed global_settings. | - | existing: tests/assert_type/db/test_connection.py |
| [#376](https://github.com/sbdchd/django-types/pull/376) | sync StrOrPromise with django-stubs | 🟡 partial | Mostly already present. Port: DecimalValidator.messages dict[str, _StrOrPromise] (lazy at runtime; core/validators.pyi:138), assertRedirects expected_url _StrOrPromise (str()-coerced; test/testcases.pyi:76), optionally URLValidator schemes Collection[str] (:57,60). Test only covers existing slugify TypeVar. | - | add: tests/assert_type/utils/test_text.py |
| [#375](https://github.com/sbdchd/django-types/pull/375) | sync request updates from django-stubs | ➖ already | Copy of django-stubs; django-stubs/http/request.pyi:47-125 is a superset (_ImmutableQueryDict GET/POST, multipart_parser_class, urlconf, exception_reporter_*). django-types keeps plain QueryDict. | - | existing: tests/assert_type/http/test_request.py |
| [#373](https://github.com/sbdchd/django-types/pull/373) | adding meta stub for session | ➖ already | contrib/sessions/base_session.pyi:20-23 already declares this Meta (django-types ported it from django-stubs #3200). | - | - |
| [#369](https://github.com/sbdchd/django-types/pull/369) | Add models.fields.Field.hidden property | ➖ already | Field.hidden: bool already declared (django-stubs/db/models/fields/__init__.pyi:153), matching runtime class attribute hidden = False. | - | - |
| [#367](https://github.com/sbdchd/django-types/pull/367) | update ty to the latest version | ➖ n/a | Tooling only. | - | - |
| [#366](https://github.com/sbdchd/django-types/pull/366) | add sync command to update files from the django-stubs repo | ➖ already | Files fetched verbatim from django-stubs master; only diffs vs current are typing vs typing_extensions TypeVar imports. Sync script/ast-grep rules are django-types tooling. | - | - |
| [#365](https://github.com/sbdchd/django-types/pull/365) | Add stubs for django.db.models.StringAgg | ➖ already | Present at django-stubs/db/models/aggregates.pyi:76 with full kwargs and re-exported at db/models/__init__.pyi:15. | - | existing: tests/assert_type/db/models/test_aggregates.py |
| [#363](https://github.com/sbdchd/django-types/pull/363) | Improve `django.db.models.query._BaseQuerySet.raw` types | ➖ already | Return type already RawQuerySet[_Model] (django-stubs/db/models/query.pyi:181-187). Skip the params hunk: tuple[Any] means a 1-tuple, while runtime takes any iterable, Mapping or None (sql/query.py params_type). | - | existing: tests/assert_type/db/models/test_queryset_row_type/models.py |
| [#362](https://github.com/sbdchd/django-types/pull/362) | Improve `django.core.management` types | 🟡 partial | Port: CommandParser.error -> NoReturn (base.pyi:26, always raises), OutputWrapper not subclassing TextIOBase (base.pyi:38, true since Django 5.2), __getattr__ -> Any, handle_app_config(AppConfig), LabelCommand.missing_args_message: str. Optional: call_command -> str \| None. | - | add: tests/assert_type/core/management/test_base.py |
| [#360](https://github.com/sbdchd/django-types/pull/360) | Allow `Q` objects to be passed to `django.db.models.Index` | ✅ yes | Runtime accepts it: Index(Q(author__isnull=False), name=...) emits (("author" IS NOT NULL)) on Django 6.1. Widen db/models/indexes.pyi:27 (and expressions attr :23) plus the postgres index subclasses (contrib/postgres/indexes.pyi:27-110). | - | - |
| [#358](https://github.com/sbdchd/django-types/pull/358) | ci: bump python & mypy versions | ➖ already | Only real hunk (startElement attrs: AttributesImpl, matching typeshed) is already at django-stubs/utils/xmlutils.pyi:14; the rest is type-ignore churn. | - | - |
| [#357](https://github.com/sbdchd/django-types/pull/357) | query: fix hint on abulk_create update_conflicts | ➖ already | Already `update_conflicts: bool = False` (django-stubs/db/models/query.pyi:138, manager.pyi:84). | - | - |
| [#353](https://github.com/sbdchd/django-types/pull/353) | Add DB comment functionality to all fields and tables | ➖ already | db_comment on FileField (fields/files.pyi:87) and related fields (related.pyi:79,134,223,296,361); JSONField takes **kwargs. Options.db_table_comment: str (options.pyi:55) matches runtime default ""; PR's \| None is looser. | - | - |
| [#351](https://github.com/sbdchd/django-types/pull/351) | refactor: Update shortcuts typing | ➖ already | Copied from django-stubs, identical to shortcuts.pyi:24-50. redirect overloads covered by tests/assert_type/test_shortcuts.py. | - | existing: tests/assert_type/test_shortcuts.py |
| [#350](https://github.com/sbdchd/django-types/pull/350) | refactor: Update dispatcher typing | ➖ already | Copied from django-stubs, identical to dispatch/dispatcher.pyi. Return elements typed `str \| None` stay wrong (#841, not fixed here). No receiver test yet. | - | add: tests/assert_type/dispatch/test_dispatcher.py |
| [#348](https://github.com/sbdchd/django-types/pull/348) | Add types for `GeneratedField` | 🟡 partial | GeneratedField exists (fields/generated.pyi:15) but lacks the expression attribute (and db_persist) set in runtime __init__; pyright errors on field.expression. Port those. Overload-based get typing is n/a. | - | - |
| [#346](https://github.com/sbdchd/django-types/pull/346) | Fix ruff errors | ➖ n/a | Lint autofix; django-stubs already annotates aliases with TypeAlias. Some fixes are wrong (CSRF_COOKIE_DOMAIN: TypeAlias = None, LogEntry.user: TypeAlias); django-stubs types these properly (conf/global_settings.pyi:458, contrib/admin/models.pyi:40). | - | - |
| [#345](https://github.com/sbdchd/django-types/pull/345) | fix: Update db model constraints | ➖ already | Port from django-stubs; django-stubs/db/models/constraints.pyi:44-96 is newer (deprecated check= dropped per Django 6.0). | - | existing: tests/assert_type/db/models/test_constraints.py |
| [#343](https://github.com/sbdchd/django-types/pull/343) | refactor: Update enums to reflect typing spec changes | ➖ already | Already in django-stubs: contrib/admin/options.pyi:46, contrib/gis/gdal/srs.pyi:6, db/models/constants.pyi, db/models/constraints.pyi:14, template/base.pyi:29. | - | - |
| [#342](https://github.com/sbdchd/django-types/pull/342) | fix: update types for module and models_module in AppConfig | ➖ already | apps/config.pyi:12,18 already use types.ModuleType \| None. | - | - |
| [#341](https://github.com/sbdchd/django-types/pull/341) | fix: Add missing db_comment to Field subclasses | ➖ already | Both inherit Field.__init__, which has db_comment: str \| None (django-stubs/db/models/fields/__init__.pyi:181). | - | - |
| [#340](https://github.com/sbdchd/django-types/pull/340) | fix: Align assertNotContains signature with Django runtime | ➖ already | django-stubs/test/testcases.pyi:97 already has response: HttpResponseBase, text: bytes \| int \| _StrOrPromise. | - | - |
| [#338](https://github.com/sbdchd/django-types/pull/338) | fix: use sequence instead of list in send_mass_mail | 🟡 partial | Outer is already Iterable (core/mail/__init__.pyi:40). The inner recipient `list[str]` should become Sequence[str], matching EmailMessage(to: Sequence[str]), which receives it at runtime. | - | - |
| [#337](https://github.com/sbdchd/django-types/pull/337) | fix: Exists(...) \| Q(...) | ➖ already | django-stubs/db/models/expressions.pyi:49,53,55 accept Combinable \| Q and return Q (PR wrongly returns Self). Untested. Separate gap: Q(...) \| Exists(...) infers Combinable via __ror__ (:64), runtime returns Q. | - | add: tests/assert_type/db/models/test_expressions.py |
| [#336](https://github.com/sbdchd/django-types/pull/336) | fix(ty): timezone.override invalid __exit__ type | ➖ already | utils/timezone.pyi:20-25 already takes `... \| None` for all three __exit__ parameters. | - | - |
| [#335](https://github.com/sbdchd/django-types/pull/335) | Allow IntegerChoices in integer like field choices | ➖ already | Integer fields inherit Field.__init__ whose choices is _ChoicesInput including type[Choices] (fields/__init__.pyi:174, utils/choices.pyi:11). | - | existing: tests/typecheck/db/models/test_fields_choices.yml |
| [#331](https://github.com/sbdchd/django-types/pull/331) | fix: Fix context manager types for all cases | ➖ already | All six targets already typed: db/backends/base/schema.pyi:68, template/context.pyi:21, test/testcases.pyi:46, test/utils.pyi:108, utils/archive.pyi:15, utils/translation/__init__.pyi:30. | - | - |
| [#330](https://github.com/sbdchd/django-types/pull/330) | fix: Preserve signature for keep_lazy_text | ➖ already | utils/functional.pyi:48 is `keep_lazy_text(func: _C) -> _C`. No assert_type test covers it yet. | - | add: tests/assert_type/utils/test_functional.py |
| [#329](https://github.com/sbdchd/django-types/pull/329) | feat: Use StrPromise to mark lazy strings | ➖ already | django-stubs has _StrPromise (utils/functional.pyi:25), and lazystr and every *gettext_lazy return it (utils/translation/__init__.pyi:17-20). | - | existing: tests/assert_type/utils/test_translation.py |
| [#327](https://github.com/sbdchd/django-types/pull/327) | fix: Context managers should use BaseException | ➖ already | django-stubs/test/utils.pyi:58 already uses type[BaseException] \| None / BaseException \| None. | - | - |
| [#326](https://github.com/sbdchd/django-types/pull/326) | [Django 5.0] ChoicesType type alias for ChoicesMeta | ➖ already | django-stubs/db/models/enums.pyi:12 defines ChoicesType as the real metaclass; ChoicesMeta was removed in Django 6.0, matching runtime. | - | - |
| [#325](https://github.com/sbdchd/django-types/pull/325) | fix: Fix invalid type for form in `construct_change_message` | ✅ yes | options.pyi:281 and utils.pyi:116 take forms.Form, so passing ModelForm (BaseForm, not Form) fails on all 4 checkers. Use BaseForm. Also accept formsets=None, which Django passes (options.py:2307, auth/admin.py:180). | - | - |
| [#323](https://github.com/sbdchd/django-types/pull/323) | functional: update stubs 1:1 with django-stubs@1.11.0 | ➖ already | Verbatim old django-stubs copy; current django-stubs/utils/functional.pyi:99-104 has classproperty (simpler, py3.11 style) and generic LazyObject/SimpleLazyObject. | - | existing: tests/assert_type/utils/test_functional.py |
| [#322](https://github.com/sbdchd/django-types/pull/322) | `BaseExpression.as_sql`: Add return types | ➖ already | django-stubs/db/models/expressions.pyi:81 returns _AsSqlType = tuple[str, tuple[_ParamT, ...]] (db/models/sql/compiler.pyi:21). | - | - |
| [#321](https://github.com/sbdchd/django-types/pull/321) | ci: poetry to uv | ➖ n/a | Tooling only; stub hunks are import reordering (db/models/__init__.pyi, fields/composite.pyi). | - | - |
| [#320](https://github.com/sbdchd/django-types/pull/320) | Support Django 5.2 additions to `django.http.request` and `django.http.response` | ➖ already | django-stubs/http/request.pyi:107 get_preferred_type (Sequence[str]), response.pyi:110 text, :129 StreamingHttpResponse.text NoReturn, :144 preserve_request. | - | - |
| [#319](https://github.com/sbdchd/django-types/pull/319) | ForeignKey fix __new__ with null True overload | ➖ n/a | Only adjusts django-types null= overloads; django-stubs has no such overloads and ForeignKey accepts default: Any (django-stubs/db/models/fields/related.pyi:209). | - | - |
| [#316](https://github.com/sbdchd/django-types/pull/316) | Add django-stub for Composite Primary Key  | 🟡 partial | composite.pyi exists, but CompositePrimaryKey(Field[Any, Any]) (fields/composite.pyi:24) reads Any. Port typed get/set, fixing the PR: CompositeAttribute.__get__ always returns a tuple. Set _pyi_private_* too, for the plugin's pk alias. | - | add: tests/assert_type/db/models/fields/test_composite_pk/models.py |
| [#315](https://github.com/sbdchd/django-types/pull/315) | A few database updates and improvements | ➖ already | All present, often stricter: db/migrations/operations/base.pyi:10-42, db/utils.pyi:27-60, utils/connection.pyi (generic handler). Only gap is untyped DatabaseErrorWrapper.wrapper attribute, not worth porting. | - | - |
| [#312](https://github.com/sbdchd/django-types/pull/312) | auth: add 5.2 async methods | ➖ already | Present in contrib/auth/backends.pyi:13-36,55, base_user.pyi:16, models.pyi:62-70,89-99 (acreate_user, ahas_perm, aconfigure_user, aget_by_natural_key, etc.). | - | - |
| [#310](https://github.com/sbdchd/django-types/pull/310) | Django 5.2, Python 3.10, update `django.contrib.admin.models` | ➖ already | contrib/admin/models.pyi:16-36 has log_actions with Literal single_object overloads (better than django-types' union return); LogEntry fields already typed. Rest is tooling/import reshuffling. Overloads lack an assert_type test. | - | add: tests/assert_type/contrib/admin/test_models.py |
| [#309](https://github.com/sbdchd/django-types/pull/309) | Fix Black formatting violations. | ➖ n/a | Formatting only. | - | - |
| [#308](https://github.com/sbdchd/django-types/pull/308) | contrib.admin.decorators: use TypeVar | ➖ already | django-stubs/contrib/admin/decorators.pyi:11-12,68-70 uses _F and a ModelAdmin-bound _ModelAdmin TypeVar, which is stricter than an unbound _T. No assert_type checks that register returns the class unchanged. | - | add: tests/assert_type/contrib/admin/test_decorators.py |
| [#307](https://github.com/sbdchd/django-types/pull/307) | Add `query` and `fragment` parameters to `reverse` type definition | ➖ already | urls/base.pyi:17-36 already has keyword-only query: QueryDict \| _QueryType \| None and fragment on both reverse and reverse_lazy. | - | - |
| [#305](https://github.com/sbdchd/django-types/pull/305) | `RequestClient.request(**extra)` META can include non-str | ➖ already | django-stubs/test/client.pyi:102 (and every method) already uses **extra: Any. | - | - |
| [#304](https://github.com/sbdchd/django-types/pull/304) | Template.render() requires Context. dict and None fails. | ➖ already | template/base.pyi:62 already declares render(self, context: Context) -> SafeString, matching runtime base.Template.render(self, context). | - | - |
| [#298](https://github.com/sbdchd/django-types/pull/298) | Add `current_app` to `HttpRequest` | ➖ already | django-stubs/http/request.pyi:74 has current_app: str and :68 user: _AnyUser, with the same middleware comments. | - | - |
| [#297](https://github.com/sbdchd/django-types/pull/297) | fix `ModelChoiceField.to_field_name` annotation | ➖ already | forms/models.pyi:281 and :292 already type to_field_name as str \| None. | - | - |
| [#296](https://github.com/sbdchd/django-types/pull/296) | Add from_queryset parameter to refresh_from_db | ➖ already | Present (django-stubs/db/models/base.pyi:85-96). | - | existing: tests/assert_type/db/models/test_base.py |
| [#293](https://github.com/sbdchd/django-types/pull/293) | AuthenticationForm.user_cache: AbstractBaseUser \| None | ➖ already | contrib/auth/forms.pyi:99 has user_cache: _User \| None (plugin-refined user alias). | - | - |
| [#291](https://github.com/sbdchd/django-types/pull/291) | add BaseEmailBackend.fail_silently bool attribute. | ➖ already | Already declared: core/mail/backends/base.pyi:8. | - | - |
| [#290](https://github.com/sbdchd/django-types/pull/290) | WSGIRequest->HttpRequest in most places for consistency. | ➖ already | django-stubs uses HttpRequest throughout, e.g. contrib/admin/sites.pyi:61, contrib/auth/middleware.pyi:8, utils/translation/__init__.pyi:42. WSGIRequest remains only in test/client and core/servers. | - | - |
| [#289](https://github.com/sbdchd/django-types/pull/289) | admin formfield_for_dbfield returns FormField, not ModelField | ➖ already | django-stubs/contrib/admin/options.pyi:133-135 already returns FormField \| None (django.forms.fields.Field). | - | - |
| [#288](https://github.com/sbdchd/django-types/pull/288) | fix some formset types (#271) | ➖ already | forms/formsets.pyi:47,59-63 use Sequence[Mapping] initial and _DataT/_FilesT; formset_factory takes form: type[_F] (formsets.pyi:116-129). No assert_type test covers formset_factory inference. | - | add: tests/assert_type/forms/test_formsets.py |
| [#286](https://github.com/sbdchd/django-types/pull/286) | fix: Third argument for ngettext_lazy is optional | ➖ already | utils/translation/__init__.pyi:19-20 default number=None. Tested in tests/assert_type/utils/test_translation.py:15. | - | - |
| [#283](https://github.com/sbdchd/django-types/pull/283) | ValidationError message argument is recursively defined | ❌ no | dict/list are invariant, so the recursive alias rejects pre-typed `dict[str, list[str]]` or `list[str]` (checked on mypy and pyright). core/exceptions.pyi:42 deliberately keeps dict[str, Any] \| list[Any]. | - | - |
| [#281](https://github.com/sbdchd/django-types/pull/281) | Allow passing None as from_email to send_mass_mail | ➖ already | Datatuple already has `str \| None` sender (core/mail/__init__.pyi:40). | - | - |
| [#278](https://github.com/sbdchd/django-types/pull/278) | Fix annotations for assertJSON* | ➖ already | django-stubs/test/testcases.pyi:181-192 already types raw as str \| bytes \| bytearray. | - | - |
| [#272](https://github.com/sbdchd/django-types/pull/272) | Fix linting and testing errors | ➖ n/a | Tooling/formatting only; no typing change. | - | - |
| [#271](https://github.com/sbdchd/django-types/pull/271) | forms/formsets: Improve types | 🟡 partial | Generic BaseFormSet and formset_factory already exist (forms/formsets.pyi:30-129). Port BaseFormSet.errors -> list[ErrorDict] (formsets.pyi:100 says list[ErrorList]; runtime appends form.errors). Optionally deletion/ordering_widget: type[Widget] (formsets.pyi:50-51). | - | add: tests/assert_type/forms/test_formsets.py |
| [#270](https://github.com/sbdchd/django-types/pull/270) | fix: Check permissions methods expects any model, not a user model only | ➖ already | contrib/auth/models.pyi:88-99 already use obj: Model \| None (sync and async). | - | - |
| [#268](https://github.com/sbdchd/django-types/pull/268) | Update transaction.pyi | ➖ already | django-stubs/db/transaction.pyi:37-42 already types __exit__ with type[BaseException]/BaseException/TracebackType \| None. No test asserts protocol compatibility; verified the snippet passes mypy, pyright, ty. | - | add: tests/assert_type/db/test_transaction.py |
| [#265](https://github.com/sbdchd/django-types/pull/265) | Fixup `db.models.fields.Field` overloads for pyright 1.1.378 | ➖ n/a | Overload machinery and pyright-ignore comments only; inserted `*` contradicts runtime positional params; django-stubs already re-exports http.cookies.SimpleCookie (django-stubs/http/cookie.pyi:1). | - | - |
| [#263](https://github.com/sbdchd/django-types/pull/263) | Add `db_default` arg to `Field` constructors | 🟡 partial | Params exist (fields/__init__.pyi:182). Port the attribute: :144 types it type[NOT_PROVIDED] \| Expression, but Django 5.2/6.1 store the raw value and wrap it only in _db_default_expression; widen with \| Any. | - | - |
| [#262](https://github.com/sbdchd/django-types/pull/262) | Fix aiterator() signature. | ➖ already | Already `def aiterator(...) -> AsyncIterator[_Row]` (django-stubs/db/models/query.pyi:115, manager.pyi:63). No assert_type coverage yet. | - | add: tests/assert_type/db/models/test_queryset_row_type/models.py |
| [#261](https://github.com/sbdchd/django-types/pull/261) | Allow text choices being directly assigned as choices. | ➖ already | _ChoicesInput includes type[Choices] (django-stubs/utils/choices.pyi:11) and is used by CharField.__init__ choices (fields/__init__.pyi:363). | - | existing: tests/typecheck/db/models/test_fields_choices.yml |
| [#260](https://github.com/sbdchd/django-types/pull/260) | KT is a function, not an instance. | ➖ already | KeyTextTransform.from_lookup -> Self (django-stubs/db/models/fields/json.pyi:97) and KT: Callable[[str], KeyTextTransform] (:99) match runtime KT = KeyTextTransform.from_lookup. | - | - |
| [#259](https://github.com/sbdchd/django-types/pull/259) | Forms and exceptions improvements | ➖ already | core/exceptions.pyi:20,33-50, forms/forms.pyi:16,89-91, forms/models.pyi:57-74, forms/utils.pyi:20-80 already cover it; ValidationError.__iter__ yields list[str] at runtime, so django-types' list[ValidationError] is wrong. Open #924 looks stale (_FilesT is MultiValueDict). | - | - |
| [#258](https://github.com/sbdchd/django-types/pull/258) | Improve types around template rendering | 🟡 partial | Port: forms/renderers.pyi:19,23 get_template Any -> _EngineTemplate, backend-specific overrides, fix :36 TemplatesSetting (base.Template\|None), loader.pyi:11 select_template, django Template.render -> SafeString. Skip Mapping contexts (make_context needs dict), Div renderers (removed 5.0). | - | add: tests/assert_type/forms/test_renderers.py |
| [#257](https://github.com/sbdchd/django-types/pull/257) | contrib/admin/options: improve types | 🟡 partial | Port only save_form(..., change: bool) -> _ModelT (options.pyi:291, now Any) and action_form: ClassVar[type[ActionForm]] (:203). Rest is already in place or wrong at runtime: Mapping context (it calls .update), changeform_view -> TemplateResponse, formsets: BaseModelFormSet. | - | add: tests/assert_type/contrib/admin/test_options.py |
| [#256](https://github.com/sbdchd/django-types/pull/256) | Add missing export of EmptyFieldListFilter to admin | ➖ already | django-stubs/contrib/admin/__init__.pyi:9 and __all__ already export EmptyFieldListFilter. | - | - |
| [#254](https://github.com/sbdchd/django-types/pull/254) | Django 4.2 + Python 3.8 | ➖ n/a | Tooling/version bump plus django-types __new__ overload ignore cleanup; nothing maps to django-stubs stubs. | - | - |
| [#250](https://github.com/sbdchd/django-types/pull/250) | Add db_comment attribute in Fields classes | ➖ already | Field.db_comment: str \| None (fields/__init__.pyi:143) and db_comment param on Field.__init__ (:181) and every overriding field __init__. | - | - |
| [#246](https://github.com/sbdchd/django-types/pull/246) | Improvements to `django.contrib.auth` | 🟡 partial | Port only AnonymousUser save/delete/set_password/check_password -> Never (always raise NotImplementedError) and (a)get_group_permissions -> set[str] (contrib/auth/models.pyi:138-141,148-149). AbstractUser returns would break custom AbstractBaseUser models; rest already. | - | add: tests/assert_type/contrib/auth/test_user_flags/models.py |
| [#245](https://github.com/sbdchd/django-types/pull/245) | test/client.pyi: Black format | ➖ n/a | Formatting only. | - | - |
| [#244](https://github.com/sbdchd/django-types/pull/244) | Add alogin, aauthenticate and update request type | ➖ already | contrib/auth/__init__.pyi:20-25 has authenticate/aauthenticate (request: HttpRequest \| None), login/alogin, alogout. | - | existing: tests/typecheck/contrib/auth/test_auth.yml |
| [#243](https://github.com/sbdchd/django-types/pull/243) | `django.core.files.storage`: Improvements | ➖ already | default_storage: Storage already (core/files/storage/__init__.pyi:23). Keep `url(name: str \| None)` (storage/base.pyi:20): FileSystemStorage.url accepts None at runtime via filepath_to_uri. | - | - |
| [#242](https://github.com/sbdchd/django-types/pull/242) | Add optional `nulls_distinct` arg to UniqueConstraint, which maps to … | ➖ already | Present on both overloads and as attribute at django-stubs/db/models/constraints.pyi:67,79,93. | - | - |
| [#241](https://github.com/sbdchd/django-types/pull/241) | django.test.client: add AsyncClient and dependencies | ➖ already | django-stubs/test/client.pyi:65 AsyncClientHandler, AsyncRequestFactory typed to ASGIRequest, :392 AsyncClient returning ASGI responses; covered in tests/assert_type/test/test_client.py. | - | existing: tests/assert_type/test/test_client.py |
| [#240](https://github.com/sbdchd/django-types/pull/240) | Add type annotation for `Q.__xor__` | ➖ already | Present at django-stubs/db/models/query_utils.pyi:52. | - | - |
| [#239](https://github.com/sbdchd/django-types/pull/239) | `db/models/fields/__init__.pyi`: Black format | ➖ n/a | Formatting only. | - | - |
| [#238](https://github.com/sbdchd/django-types/pull/238) | `django.utils.deconstruct`: Improve types | ➖ already | utils/deconstruct.pyi:15-18 has equivalent overloads (bare class and path= factory). No assert_type test covers it yet. | - | add: tests/assert_type/utils/test_deconstruct.py |
| [#236](https://github.com/sbdchd/django-types/pull/236) | Add headers parameter to django.test.{RequestFactory,Client} methods | ➖ already | django-stubs/test/client.pyi:84-200 has headers: Mapping[str, str] \| None on __init__ and all _RequestFactory/Client/AsyncClient methods, plus query_params. | - | - |
| [#235](https://github.com/sbdchd/django-types/pull/235) | Add ManyToManyRelatedManager to auth models | ❌ no | The plugin skips reverse accessors already declared (mypy_django_plugin/transformers/models.py:526), so stub declarations would replace its precise types (concrete AUTH_USER_MODEL, through model). user_set also depends on the swappable user model. | - | - |
| [#234](https://github.com/sbdchd/django-types/pull/234) | Add another overload to path function | ➖ already | urls/conf.pyi:10 _IncludedURLConf = tuple[Sequence[URLResolver \| URLPattern], str \| None, str \| None]; covariant tuple/Sequence already accepts tuple[list[...], str, str] via the overload at conf.pyi:30. | - | existing: tests/assert_type/urls/test_conf.py |
| [#232](https://github.com/sbdchd/django-types/pull/232) | Class property `Choices.values` returns list of Members | ❌ no | Wrong vs runtime: ChoicesType.values returns member.value (raw int/str/tuple), not members, so `.values[0].go()` crashes. django-stubs/db/models/enums.pyi:41-70 correctly returns list[int]/list[str]. | - | - |
| [#230](https://github.com/sbdchd/django-types/pull/230) | fix `applied_migrations` typing of recorder.pyi | ➖ already | django-stubs/db/migrations/recorder.pyi:21 returns dict[tuple[str, str], Migration], more precise than the PR's Any value. | - | - |
| [#229](https://github.com/sbdchd/django-types/pull/229) | Add new model field choices options | ➖ already | Field.__init__ choices is _ChoicesInput (fields/__init__.pyi:174), which covers mapping, Choices class and callable (django-stubs/utils/choices.pyi:9-12). | - | existing: tests/typecheck/db/models/test_fields_choices.yml |
| [#228](https://github.com/sbdchd/django-types/pull/228) | Allow `datetime - F("datetime")` expression | ➖ already | django-stubs/db/models/expressions.pyi:22,58: _SubOperand includes datetime/timedelta for __rsub__. | - | existing: tests/assert_type/db/models/test_expressions.py |
| [#227](https://github.com/sbdchd/django-types/pull/227) | Add `abulk_update` | ➖ already | Present on QuerySet (django-stubs/db/models/query.pyi:143) and Manager (manager.pyi:89). | - | - |
| [#224](https://github.com/sbdchd/django-types/pull/224) | Add allow_unicode to SlugField | ➖ already | SlugField.__init__ already has keyword allow_unicode: bool = False (django-stubs/db/models/fields/__init__.pyi:403). | - | - |
| [#222](https://github.com/sbdchd/django-types/pull/222) | `django-stubs/template/library.pyi` Improvements | ➖ already | template/library.pyi:19-94 already overloads every decorator with a bound Callable TypeVar preserving the signature, including simple_block_tag and inclusion_tag. Open PR #1904 (takes_context) is related but different work. | - | existing: tests/assert_type/template/test_library.py |
| [#221](https://github.com/sbdchd/django-types/pull/221) | Improve django.forms | ➖ already | forms/forms.pyi:17-31,76,84-86 and forms/boundfield.pyi:26-29 already have these (or better: Iterable field_order, cached_property subwidgets, Iterator). No BaseForm.Meta in django-stubs. | - | - |
| [#219](https://github.com/sbdchd/django-types/pull/219) | Improve types for get_formset and get_template | ➖ already | manager.pyi:39 from_queryset -> type[Self]; backends/django.pyi:26 defines Template; loader.pyi:10 returns the _EngineTemplate protocol, more correct since any backend's Template can be returned. | - | existing: tests/assert_type/db/models/test_managers.py |
| [#218](https://github.com/sbdchd/django-types/pull/218) | fix: Add `get_inlines` method to BaseModelAdmin | ➖ already | django-stubs/contrib/admin/options.pyi:154-156 (plus InlineModelAdmin override :385) already has get_inlines. | - | - |
| [#217](https://github.com/sbdchd/django-types/pull/217) | improve: Add missing 'aget_many' and 'aset_many' in BaseCache | ➖ already | Both exist: core/cache/backends/base.pyi:41,56. | - | - |
| [#215](https://github.com/sbdchd/django-types/pull/215) | fix: Remove `Meta` from `Model` | ➖ already | django-stubs Model declares no Meta (django-stubs/db/models/base.pyi:57-71). | - | - |
| [#213](https://github.com/sbdchd/django-types/pull/213) | django/test/utils.py polish | 🟡 partial | Only missing piece: decorate_class keeps the class type (utils.pyi:64 returns _TestClass, override_settings utils.pyi:75 returns bare type). Low value, direct calls are rare. __call__ (utils.pyi:66), __enter__ Self, tag, setup_databases already better; generic ContextList not worth it. | - | add: tests/assert_type/test/test_utils.py |
| [#212](https://github.com/sbdchd/django-types/pull/212) | fix: Use Any for HttpResponse content argument | ➖ already | django-stubs/http/response.pyi:102 already takes content: object, and the content setter accepts object via _PropertyDescriptor[object, bytes] (response.pyi:96). | - | - |
| [#210](https://github.com/sbdchd/django-types/pull/210) | Improve `django.template` | 🟡 partial | Port only select_template's return (template/loader.pyi:11 is Any), typed _EngineTemplate like get_template, not base.Template. get_template/get_app_template_dirs already better. __iter__ -> BaseEngine is wrong: runtime iterates aliases (str). | - | add: tests/assert_type/template/test_loader.py |
| [#208](https://github.com/sbdchd/django-types/pull/208) | Improve `django.http` types | 🟡 partial | Port only get_signed_cookie default TypeVar, as overloads: no default -> str, default: _Z -> str \| _Z (request.pyi:83 returns str \| None). Optional: to_wsgi_names/to_asgi_names Mapping[str, _V] -> dict[str, _V] (request.pyi:43). Rest already; encoding -> str is wrong (_encoding defaults None). | - | add: tests/assert_type/http/test_request.py |
| [#206](https://github.com/sbdchd/django-types/pull/206) | Update db.models.functions.comparison | ➖ already | Collate at django-stubs/db/models/functions/comparison.pyi:27; JSONObject in functions/json.pyi, re-exported at functions/__init__.pyi:3,32. | - | - |
| [#205](https://github.com/sbdchd/django-types/pull/205) | Improve BaseManager, Manager types | ➖ already | deconstruct identical (django-stubs/db/models/manager.pyi:34-36); from_queryset returns type[Self], better than type[Manager[_T]] (manager.pyi:39). The _queryset_class hunk is superseded by #423's corrected type[QuerySet[Any, Any]], handled there. | - | existing: tests/assert_type/db/models/test_managers.py |
| [#201](https://github.com/sbdchd/django-types/pull/201) | fix: fix bulk_create and abulk_create annotations | ➖ already | Already `update_conflicts: bool = False` and `unique_fields: Collection[str] \| None` on QuerySet and Manager (django-stubs/db/models/query.pyi:124-141). | - | - |
| [#199](https://github.com/sbdchd/django-types/pull/199) | Add Model.validate_constraints | ➖ already | Already present (django-stubs/db/models/base.pyi:140). | - | - |
| [#198](https://github.com/sbdchd/django-types/pull/198) | Allow NoneType for ModelAdmin.actions | ➖ already | django-stubs/contrib/admin/options.pyi:202 types actions as Sequence[...] \| None. | - | - |
| [#197](https://github.com/sbdchd/django-types/pull/197) | Support ValuesQuerySet in assertQuerySetEqual | ➖ n/a | ValuesQuerySet is a django-types-only class. django-stubs encodes rows as QuerySet[_M, _Row], so the PR 189 port (qs: Iterable[_T], transform: Callable[[_T], Any]) covers values_list + transform=tuple without an overload. | - | - |
| [#196](https://github.com/sbdchd/django-types/pull/196) | Use updated types-psycopg2 from typeshed | ➖ n/a | psycopg2 tooling. django-stubs already relies on types-psycopg2 (pyproject.toml dependency groups). | - | - |
| [#192](https://github.com/sbdchd/django-types/pull/192) | Fix return types of encoding utilities | ➖ already | utils/encoding.pyi:15-47 has precise overloads (str/bytes plus strings_only passthrough). Covered by tests/assert_type/utils/test_encoding.py. | - | existing: tests/assert_type/utils/test_encoding.py |
| [#191](https://github.com/sbdchd/django-types/pull/191) | Make `RelatedManager` and `ManyToManyRelatedManager` callable | ➖ already | Both already define `__call__(self, *, manager: str)` (django-stubs/db/models/fields/related_descriptors.pyi:110,171), matching runtime. | - | existing: tests/typecheck/fields/test_related.yml |
| [#190](https://github.com/sbdchd/django-types/pull/190) | Make managers in `django.contrib` generic | 🟡 partial ⏸ deferred | Port generic Log/Permission/Group/SiteManager with `objects: ClassVar[XManager[Self]]` (contrib/auth/models.pyi:33-52, sites/models.pyi:8-14, admin/models.pyi:16-46): mypy gives Group for ProxyGroup.objects.get(). Also Session overrides (sessions/models.pyi:7). Rest already. #2590/#2214 do Session.objects only. |  (in flight: [#2590](https://github.com/typeddjango/django-stubs/pull/2590)) | add: tests/assert_type/contrib/auth/test_models.py |
| [#189](https://github.com/sbdchd/django-types/pull/189) | Add TransactionTestCase.assertQuerySetEqual | ✅ yes | testcases.pyi:201 types transform as Callable[[Model], Any]: mypy rejects lambda u: u.username, (Blog) -> str functions and transform=tuple on values_list (verified). Port as qs: Iterable[_T], transform: Callable[[_T], Any] \| None, which also covers PR 197. | - | add: tests/assert_type/test/test_testcase.py |
| [#187](https://github.com/sbdchd/django-types/pull/187) | Enable remaining ruff rules | ➖ already | django-stubs enables all PYI rules (pyproject.toml:158) and already annotates __eq__ other as object (contrib/gis/measure.pyi:17, contrib/gis/geos/mutable_list.pyi:17, contrib/gis/gdal/geomtype.pyi:10). | - | - |
| [#185](https://github.com/sbdchd/django-types/pull/185) | Use PEP-604 syntax for unions | ➖ already | AST diff with unions normalized shows only Union[Literal[1], Literal[2]] to Literal[1, 2]; django-stubs has no Optional[/Union[ left in django-stubs/**/*.pyi. | - | - |
| [#184](https://github.com/sbdchd/django-types/pull/184) | Use PEP-585 standard generic collections | ➖ already | AST diff with typing names normalized shows zero semantic change; django-stubs already uses PEP 585 builtins throughout. | - | - |
| [#183](https://github.com/sbdchd/django-types/pull/183) | Use Self type from PEP 673 everywhere | ➖ already | django-stubs uses Self in the same places (db/models/query.pyi:211, core/files/base.pyi:24,54, contrib/postgres/search.pyi:81-84, utils/safestring.pyi:10); only metaclass _Self remains (db/models/base.pyi:16), where Self can't apply. | - | existing: tests/typecheck/managers/querysets/test_basic_methods.yml |
| [#181](https://github.com/sbdchd/django-types/pull/181) | fix: fix objects attribute for pyright 1.1.324 | ➖ n/a | objects on Model is django-types design; django-stubs uses ModelBase.__getattr__ plus the plugin (django-stubs/db/models/base.pyi:55). ClassVar contrib managers and `_meta: ClassVar[Options[Self]]` (base.pyi:68) already exist; rest is formatting/tooling. | - | - |
| [#176](https://github.com/sbdchd/django-types/pull/176) | Add Deferrable | ➖ already | Present at django-stubs/db/models/constraints.pyi:14-16,66,76 and db/models/__init__.pyi:22. | - | - |
| [#172](https://github.com/sbdchd/django-types/pull/172) | Added the durable parameter in Atomic decorator and context-manager | ➖ already | Present at django-stubs/db/transaction.pyi:33,50. | - | existing: tests/assert_type/db/test_transaction.py |
| [#170](https://github.com/sbdchd/django-types/pull/170) | Add typing to Graph and Node | 🟡 partial | node_map/nodes already typed (graph.pyi:32-33, nodes even allows None). Port only Node.children/parents set[Any] -> set[Node] (graph.pyi:10-11); runtime add_child/add_parent only store Nodes. | - | - |
| [#169](https://github.com/sbdchd/django-types/pull/169) | feat: Add ModelAdmin.get_formset_kwargs typing | ➖ already | django-stubs/contrib/admin/options.pyi:343-345 has get_formset_kwargs with a typed InlineModelAdmin[Any, _ModelT] inline. | - | - |
| [#168](https://github.com/sbdchd/django-types/pull/168) | Add `permission_set` reverse lookup to ContentType. | ➖ n/a | Plugin-less workaround: the mypy plugin adds reverse managers; contrib stubs declare none (contrib/contenttypes/models.pyi:15-27). Hardcoding would couple contenttypes to auth being installed and mistype it as Manager, not RelatedManager. | - | - |
| [#167](https://github.com/sbdchd/django-types/pull/167) | Update the return type of bulk_update from None to int | ➖ already | bulk_update/abulk_update already return int (django-stubs/db/models/query.pyi:142-145); full_clean already has validate_constraints (db/models/base.pyi:141-143). | - | existing: tests/assert_type/db/models/test_queryset_row_type/models.py |
| [#165](https://github.com/sbdchd/django-types/pull/165) | Add RenameIndex migrate operation | ➖ already | Present at django-stubs/db/migrations/operations/models.pyi:138-153, using cached_property like runtime. | - | - |
| [#163](https://github.com/sbdchd/django-types/pull/163) | GenericIPAddressField unpack_ipv4 should be bool | ➖ already | Already bool for attribute and param: django-stubs/db/models/fields/__init__.pyi:495 and :502. | - | - |
| [#162](https://github.com/sbdchd/django-types/pull/162) | Add a _meta property to BaseForm | ❌ no | Runtime BaseForm has no _meta; only ModelForms do, as ModelFormOptions (not model Options). django-stubs has _meta: ModelFormOptions[_M] on BaseModelForm (forms/models.pyi:74); django-types itself reverted this in #259. | - | - |
| [#159](https://github.com/sbdchd/django-types/pull/159) | feat: support for Django 4.2 | 🟡 partial | Port only staff_member_required: the first overload's `view_func: _C = ...` default makes `staff_member_required(login_url=...)` infer Never/Unknown (contrib/admin/views/decorators.pyi:10). Drop it and mirror login_required's _VIEW / Callable[[_VIEW], _VIEW]. Other hunks: already or n/a. | - | add: tests/assert_type/contrib/admin/views/test_decorators.py |
| [#157](https://github.com/sbdchd/django-types/pull/157) | add type parameter to queryset.as_manager | ➖ already | Already `def as_manager(cls) -> Manager[_Model]` (django-stubs/db/models/query.pyi:93); mypy's plugin replaces it with a generated ManagerFromX class, so an assert_type check would not hold on mypy. | - | existing: tests/typecheck/managers/querysets/test_as_manager.yml |
| [#156](https://github.com/sbdchd/django-types/pull/156) | Replace exception classes with ClassVars | ➖ already | Already `Final[type[ObjectDoesNotExist]]` etc. (django-stubs/db/models/base.pyi:64-66); the plugin adds per-model exception subclasses with the right hierarchy. | - | - |
| [#155](https://github.com/sbdchd/django-types/pull/155) | Fix assertQuerysetEqual annotations | ➖ already | Deprecated assertQuerysetEqual was removed in Django 5.1; django-stubs/test/testcases.pyi:201 assertQuerySetEqual already takes values: Iterable[Any] and a wider qs. Transform typing handled under PR 189. | - | - |
| [#154](https://github.com/sbdchd/django-types/pull/154) | Updates django.contrib.postgres.indexes types | ➖ already | django-stubs/contrib/postgres/indexes.pyi:24-125 already has typed *expressions on every index class and OpClass (stricter than the PR's Any). | - | - |
| [#151](https://github.com/sbdchd/django-types/pull/151) | Add some missing typings | ➖ already | Index include already typed `Sequence[str] \| None` (django-stubs/db/models/indexes.pyi:33; django-types' Optional[str] is wrong). QuerySet.alias already present (db/models/query.pyi:227). | - | - |
| [#149](https://github.com/sbdchd/django-types/pull/149) | Add missing admin filter and fix model indexes | ➖ already | EmptyFieldListFilter at django-stubs/contrib/admin/filters.pyi:131; Index expressions/contains_expressions at db/models/indexes.pyi:23-36; other hunks are formatting. | - | existing: tests/assert_type/db/models/test_indexes.py |
| [#145](https://github.com/sbdchd/django-types/pull/145) | fix: Add Model._meta typing | ➖ already | Already `_meta: ClassVar[Options[Self]]` (django-stubs/db/models/base.pyi:68), which is stricter. | - | existing: tests/assert_type/db/models/test_manager_access/models.py |
| [#140](https://github.com/sbdchd/django-types/pull/140) | fix: Add enable_nav_sidebar to AdminSite | ➖ already | django-stubs/contrib/admin/sites.pyi:38 has enable_nav_sidebar: bool. | - | - |
| [#138](https://github.com/sbdchd/django-types/pull/138) | Fix model signals | ➖ already | django-stubs/db/models/signals.pyi:19,26 already accept `_AnyHashable \| None`, broader and matching runtime. | - | - |
| [#137](https://github.com/sbdchd/django-types/pull/137) | Add type annotation to django.contrib.admin.site | ➖ already | django-stubs/contrib/admin/sites.pyi:87 declares site: AdminSite. | - | - |
| [#134](https://github.com/sbdchd/django-types/pull/134) | Make get_user_model return Type[AbstractBaseUser] instead of Type[Model] | ➖ already | contrib/auth/__init__.pyi:26 returns _UserModel = type[AbstractBaseUser] (contrib/auth/models.pyi:19-21), refined to AUTH_USER_MODEL by the mypy plugin. | - | existing: tests/typecheck/contrib/auth/test_auth.yml |
| [#133](https://github.com/sbdchd/django-types/pull/133) | Add type annotations to model signals | ➖ already | Identical in django-stubs/db/models/signals.pyi:10,31-39. | - | - |
| [#132](https://github.com/sbdchd/django-types/pull/132) | fix: Fix type for ManyToManyRelatedManager.through | ➖ already | ManyRelatedManager.through is already `type[_Through]` (django-stubs/db/models/fields/related_descriptors.pyi:170); the plugin fills in the implicit through model. | - | existing: tests/typecheck/fields/test_related.yml |
| [#131](https://github.com/sbdchd/django-types/pull/131) | fix: Add `through` to ManyToManyField | ➖ already | Runtime field has no through attribute (it's remote_field.through, typed reverse_related.pyi:130). Class access returns ManyToManyDescriptor with through -> type[_Through] (related_descriptors.pyi:152-153). Only mypy yml covers it. | - | add: tests/assert_type/db/models/fields/test_related_descriptors.py |
| [#130](https://github.com/sbdchd/django-types/pull/130) | fix: Fix type errors after upgrading pyright to 1.1.271 in `path` function with async views from `channels` | ❌ no | Loosens every async view to allow returning None, which Django's handler rejects at runtime (check_response ValueError). Channels-only pyright workaround; urls/conf.pyi:22-28 keeps Coroutine[..., HttpResponseBase]. | - | - |
| [#127](https://github.com/sbdchd/django-types/pull/127) | Improve annotations of BaseCache.get_many and format_html_join | ➖ already | get_many takes Iterable[Any] (core/cache/backends/base.pyi:40), format_html_join takes Iterable[Iterable[Any]] (utils/html.pyi:27). | - | - |
| [#120](https://github.com/sbdchd/django-types/pull/120) | feat: Add typings for async interface released for Django 4.1 | ➖ already | All present with correct AsyncIterator for aiterator (django-stubs/db/models/query.pyi:101,115-180,285). Async row types are only covered by mypy yml (test_iteration.yml); snippet passes all 4 checkers. | - | add: tests/assert_type/db/models/test_queryset_row_type/models.py |
| [#119](https://github.com/sbdchd/django-types/pull/119) | Allow `Any` in upload_to callback | ➖ already | _UploadToCallable[Any] (files.pyi:55-68) already accepts callbacks annotated with a concrete model, positional-only, returning str or PathLike. | - | add: tests/assert_type/db/models/fields/test_files.py |
| [#118](https://github.com/sbdchd/django-types/pull/118) | fix(core.files.base): Fix __exit__ return type | ➖ already | core/files/base.pyi:26-31 already returns None. | - | - |
| [#109](https://github.com/sbdchd/django-types/pull/109) | fix: add missing `db_table` argument to ManyToManyField | ➖ already | Present: db_table: str \| None = None at django-stubs/db/models/fields/related.pyi:338. | - | - |
| [#108](https://github.com/sbdchd/django-types/pull/108) | Update dependencies and fix typing issues | 🟡 partial | Port only source_is_geography -> bool: runtime returns geo_field.geography and srid == 4326, stub still Any (contrib/gis/db/models/functions.pyi:116). output_field (:114-115), ImmutableList.__new__ Self (utils/datastructures.pyi:112) already there. | - | - |
| [#105](https://github.com/sbdchd/django-types/pull/105) | Set correct types if `upload_to` is a function | ➖ already | django-stubs uses _UploadToCallable protocol (instance, filename) -> StrPath (files.pyi:55-68), better than both. Callable shape lacks assert_type coverage; verified snippet passes all 4 checkers. | - | add: tests/assert_type/db/models/fields/test_files.py |
| [#102](https://github.com/sbdchd/django-types/pull/102) | Fix fields | ➖ n/a | Only touches overload signatures; the upload_to Callable[[], Any] change is wrong (runtime calls upload_to(instance, filename)) and django-stubs has a proper protocol (files.pyi:55-63). |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| [#99](https://github.com/sbdchd/django-types/pull/99) | Missing types | ➖ already | All present: contrib/gis/admin/__init__.pyi, gis/admin/options.pyi:20, db/models/__init__.pyi:87, urls/conf.pyi:26 (Coroutine overload), utils/decorators.pyi:30-32. | - | - |
| [#98](https://github.com/sbdchd/django-types/pull/98) | Django Admin Actions can return a response | ➖ already | django-stubs/contrib/admin/options.pyi:175 _ActionCallable returns HttpResponseBase \| None, used by actions at :202. | - | existing: tests/assert_type/contrib/admin/test_decorators.py |
| [#97](https://github.com/sbdchd/django-types/pull/97) | Improve and simplify field typing overloads | ➖ n/a | Overload rewrite (see #3317). Other hunks already here (db_collation, through, to_field, db_constraint) or wrong (allow_filters typo, unpack_ipv4: str, width_field: str, upload_to: str). Literal flags on ForeignKey clash with OneToOneField/GenericRelation runtime overrides. |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| [#94](https://github.com/sbdchd/django-types/pull/94) | Missing types | ➖ already | All present or better: contrib/postgres/expressions.pyi:10, core/cache/backends/base.pyi:31-60, db/models/query.pyi:177,216,304 (3-param generic Prefetch), db/models/sql/query.pyi:56. | - | - |
| [#93](https://github.com/sbdchd/django-types/pull/93) | Add algorithm argument to signing.Signer | ➖ already | Signer.algorithm and keyword-only `algorithm: str \| None` already in core/signing.pyi:48-55. | - | - |
| [#90](https://github.com/sbdchd/django-types/pull/90) | fix: Fix signature for GenericRelation | ➖ n/a | Works around django-types' `__new__`-overloaded fields. django-stubs' GenericRelation (contrib/contenttypes/fields.pyi:93) has no `__new__` and a correct `__init__`. | - | - |
| [#89](https://github.com/sbdchd/django-types/pull/89) | fix: apps.get_model now returns a Model | ❌ no | `type[Any]` is the deliberate fallback (django-stubs/apps/registry.pyi:30); the plugin narrows literal names (mypy_django_plugin/transformers/apps.py:35). type[Model] would break field access on historical models in migrations, which is the main get_model use. | - | - |
| [#88](https://github.com/sbdchd/django-types/pull/88) | fix: Fix argument ordering for FileField | ➖ already | Already in runtime order at django-stubs/db/models/fields/files.pyi:64-69. | - | - |
| [#82](https://github.com/sbdchd/django-types/pull/82) | Allow adding and removing field values (typically primary keys) in many-to-many relationships. | ➖ already | ManyRelatedManager.add/remove already accept `_To \| int` (django-stubs/db/models/fields/related_descriptors.pyi:174,182). django-types used `_V`, the through model, which Django rejects with TypeError (related_descriptors.py:1521). Non-int pks (#1266) remain unfixed by this PR. | - | - |
| [#80](https://github.com/sbdchd/django-types/pull/80) | Add db_table kwarg to ManyToManyField constructor | ➖ already | Present: db_table: str \| None = None at django-stubs/db/models/fields/related.pyi:338. | - | - |
| [#79](https://github.com/sbdchd/django-types/pull/79) | Fix migration issues for fields with choices | ➖ n/a | Errors came from django-types' null/choices overloads; that migration snippet passes all 4 checkers here. Variance is correct (fields/__init__.pyi:53-55, related.pyi:37-39); invariance would weaken field subtyping. | - | - |
| [#77](https://github.com/sbdchd/django-types/pull/77) | Correct JSON encoder decoder types | ➖ already | Already type[json.JSONEncoder] \| None and type[json.JSONDecoder] \| None for attributes and params (fields/json.pyi:23-30); django-types even kept decoder as JSONEncoder. | - | - |
| [#73](https://github.com/sbdchd/django-types/pull/73) | Update pyright and mypy and fix all new issues they detected | ➖ n/a | Tooling bump with trivial churn; _lru_cache_wrapper takes one param so that hunk is wrong; django-stubs types check_for_language as a function (utils/translation/trans_real.pyi:66). | - | - |
| [#69](https://github.com/sbdchd/django-types/pull/69) | Allow DateField to be Optional | ➖ n/a | Nullability comes from the plugin plus _pyi_private_* (fields/__init__.pyi:525-527); __init__ null overloads are django-types design. Plugin-less null typing is in flight in #3317. |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| [#67](https://github.com/sbdchd/django-types/pull/67) | Update ProtectedError and RestrictedError stubs | ➖ already | Identical in django-stubs/db/models/deletion.pyi:69-75. | - | - |
| [#66](https://github.com/sbdchd/django-types/pull/66) | Array field | ➖ n/a | Plugin already infers element type (mypy_django_plugin/transformers/fields.py:169); plugin-less inference via null overloads is django-types design, tackled by open #3317. size already int \| None (contrib/postgres/fields/array.pyi:31). |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| [#65](https://github.com/sbdchd/django-types/pull/65) | Fields typing improvements | 🟡 partial | Port only FilePathField.path: Any -> str \| Callable[..., str] (fields/__init__.pyi:630, matches runtime self.path). Rest: overloads (see #3317), wrong (TextField(CharField), _Choice label str, DecimalField auto_now, IPv4Address set type) or already. |  (in flight: [#3317](https://github.com/typeddjango/django-stubs/pull/3317)) | - |
| [#64](https://github.com/sbdchd/django-types/pull/64) | Improve typing on JSONField | ➖ already | JSONField is Field[_ST, _GT] (fields/json.pyi:22) so JSONField[S, G]() types the value; encoder/decoder already typed (json.pyi:23-30). default/choices tied to _A is overload machinery. No assert_type coverage of explicit args. | - | add: tests/assert_type/db/models/fields/test_json.py |
| [#63](https://github.com/sbdchd/django-types/pull/63) | Improve related fields and many to many typing | ➖ n/a | Field null overloads are django-types design. Already present: ManyToManyField[_To,_Through] and ManyRelatedManager with through_defaults (django-stubs/db/models/fields/related_descriptors.pyi:165), typed deletion handlers (db/models/deletion.pyi:13). Its QuerySet arg to add() is wrong at runtime. | - | - |
| [#62](https://github.com/sbdchd/django-types/pull/62) | Update deps | ➖ n/a | Lint/dependency churn; the only typing tweak (unittest TestCase in startTest) is already how django-stubs/test/runner.pyi:7 imports TestCase. | - | - |
| [#60](https://github.com/sbdchd/django-types/pull/60) | fix(poetry): build / publish setup | ➖ n/a | Pure packaging: 681 pure renames, no stub content change. | - | - |
| [#57](https://github.com/sbdchd/django-types/pull/57) | Update pyright to the latest version | ➖ n/a | Tooling bump; enum/annotation style already modern (contrib/gis/gdal/srs.pyi:6, template/base.pyi:29). handler: FileHandler is wrong, runtime uses StreamHandler(io.StringIO()) (test/runner.pyi:20 already StreamHandler). | - | - |
| [#54](https://github.com/sbdchd/django-types/pull/54) | Improve objects inside Model | 🟡 partial | Port only `Options.model: type[_M]` (django-stubs/db/models/options.pyi:83, now type[Model]; all 4 checkers give type[Model]). ModelBase.objects n/a (base.pyi:55); _meta/default_manager already; proxy_for_model/concrete_model are parents, not _M; ContentTypeManager->BaseManager wrong. | - | add: tests/assert_type/db/models/test_base.py |
| [#49](https://github.com/sbdchd/django-types/pull/49) | timeout can be None in cache functions | ➖ already | timeout is already `float \| None` throughout core/cache/backends/base.pyi:25-58. | - | - |
| [#47](https://github.com/sbdchd/django-types/pull/47) | ref(django): cache types to be more strict | ➖ already | cache: BaseCache already (core/cache/__init__.pyi:25). Rest is wrong: DEFAULT_TIMEOUT is object() at runtime (Any at backends/base.pyi:11), and keys can be any object, so they stay Any. | - | - |
| [#42](https://github.com/sbdchd/django-types/pull/42) | fix(django): contrib.auth.models.User.objects, Manager -> UserManager | ➖ already | Already covered by `objects: ClassVar[UserManager[Self]]` on AbstractUser (django-stubs/contrib/auth/models.pyi:117). Self-bound ClassVar manager has no assert_type check; snippet passes all 4 checkers. | - | add: tests/assert_type/contrib/auth/test_models.py |
| [#41](https://github.com/sbdchd/django-types/pull/41) | Add new exceptions from Django 3.2 | ➖ already | All three exist: django-stubs/core/exceptions.pyi:22-23,55. | - | - |
| [#40](https://github.com/sbdchd/django-types/pull/40) | Expose new admin decorators in django.contrib.admin | ➖ already | django-stubs/contrib/admin/__init__.pyi:2-3 already re-exports action and display (also in __all__). | - | - |
| [#37](https://github.com/sbdchd/django-types/pull/37) | Add stubs for new admin decorators | ➖ already | django-stubs/contrib/admin/decorators.pyi:14-67 has better overloads returning the decorated _F (signature preserved), plus description_plural/location and boolean/empty_value exclusivity. No assert_type checks the preserved signature yet. | - | add: tests/assert_type/contrib/admin/test_decorators.py |
| [#36](https://github.com/sbdchd/django-types/pull/36) | Add `objects` manager to django.contrib.auth.models.User | ➖ already | AbstractUser already declares `objects: ClassVar[UserManager[Self]]` (django-stubs/contrib/auth/models.pyi:117); verified mypy, pyright, pyrefly and ty resolve User.objects to UserManager[User]. | - | - |
| [#35](https://github.com/sbdchd/django-types/pull/35) | Add stub for django.contrib.postgres.operations.AddIndexConcurrently | ➖ already | Present at django-stubs/contrib/postgres/operations.pyi:40 (NotInTransactionMixin, AddIndex), inheriting AddIndex.__init__; the PR's `index: str \| Index` is wrong anyway since AddIndex needs an Index. | - | - |
| [#32](https://github.com/sbdchd/django-types/pull/32) | Add PositiveBigIntegerField | ➖ already | Present with correct runtime bases: fields/__init__.pyi:296 (PositiveIntegerRelDbTypeMixin, BigIntegerField), exported at db/models/__init__.pyi:83. Null overloads are django-types machinery. | - | - |
| [#30](https://github.com/sbdchd/django-types/pull/30) | fix(django): overload issues with __new__ / __init__ combo | ➖ already | django-stubs Field has no __new__; AutoField (fields/__init__.pyi:685) and SearchVectorField/SearchQueryField (contrib/postgres/search.pyi:39-40) inherit the full Field.__init__. | - | - |
| [#28](https://github.com/sbdchd/django-types/pull/28) | ref(django): stricter MultiValueDict getlist default arg | ➖ already | django-stubs/utils/datastructures.pyi:84 has getlist(key, default: _Z \| None = None) -> list[_V] \| _Z, more precise; covered at tests/assert_type/utils/test_datastructures.py:25. | - | existing: tests/assert_type/utils/test_datastructures.py |
| [#26](https://github.com/sbdchd/django-types/pull/26) | ref(django): test Client types | ➖ already | django-stubs/http/cookie.pyi:1 re-exports SimpleCookie; test/client.pyi:84-200 types every method with headers/query_params and **extra: Any, which accepts QUERY_STRING and other META keys. | - | - |
| [#18](https://github.com/sbdchd/django-types/pull/18) | update: run pyright against tests | ➖ n/a | __new__ field typing is django-types' plugin-less design; dropping encoding/mark_safe overloads would regress django-stubs (utils/encoding.pyi:16-22, utils/safestring.pyi:24-28). Rest is pyright config. | - | - |
| [#15](https://github.com/sbdchd/django-types/pull/15) | 14/export jsonfield from models | ➖ already | Already exported: django-stubs/db/models/__init__.pyi:97 and listed in __all__ (:183). | - | - |
| [#10](https://github.com/sbdchd/django-types/pull/10) | add(django): type csrf and vary decorators | ✅ yes | csrf.pyi:7,11,15 are module-level Callable[[_F], _F] vars: pyright infers Any, ty errors (Expected TypeVar), verified. Same fix needed for http.pyi:13-15 require_*, conditional_page, gzip.pyi:8. vary already. |  (in flight: [#2164](https://github.com/typeddjango/django-stubs/pull/2164)) | add: tests/assert_type/views/test_decorators.py |
| [#8](https://github.com/sbdchd/django-types/pull/8) | add(django): type more decorators | ➖ already | views/decorators/cache.pyi:8-12, debug.pyi:10-11, http.pyi:17-21 already _F-preserving. decorator_from_middleware returns _ViewDecorator by design (#3080, utils/decorators.pyi:27-28, tested). auth admin *_m helpers no longer exist in Django 6.1. | - | add: tests/assert_type/views/test_decorators.py |
| [#4](https://github.com/sbdchd/django-types/pull/4) | fix: errors surfaced by pyright | ➖ already | NamedTuple classes exist (db/backends/base/introspection.pyi:11,15; db/models/query_utils.pyi:30; db/models/sql/query.pyi:17; template/defaulttags.pyi:82); from_db/complex_filter return Self (db/models/base.pyi:73-80, db/models/query.pyi:211). Field TypeVar bounds are django-types design. | - | - |
| [#3](https://github.com/sbdchd/django-types/pull/3) | fix(ci): use setuptools for building | ➖ n/a | Build/CI tooling only; _NamedTupleAnyAttr no longer exists in django-stubs (row typing handled by the plugin). | - | - |
| [#2](https://github.com/sbdchd/django-types/pull/2) | fix(django): add missing generic types params | ➖ already | django-stubs type-checks its stubs with strict + disallow_any_generics (mypy.ini:7, justfile mypy-self); HttpHeaders(CaseInsensitiveMapping[str]) at django-stubs/http/request.pyi:32. Remaining hunks (_M bound Optional[Model]) are django-types design. | - | add: tests/assert_type/http/test_request.py |

## Proposed tests

### [#426](https://github.com/sbdchd/django-types/pull/426) Type prefetch_related lookups and infer Prefetch models

add: tests/assert_type/db/models/test_query.py

```python
from django.contrib.auth.models import Group, Permission
from django.db.models import Prefetch


def prefetch_related_keeps_the_queryset_type(groups: QuerySet[Group], perms: QuerySet[Permission]) -> None:
    prefetch = Prefetch("permissions", queryset=perms)
    assert_type(prefetch.queryset, QuerySet[Permission] | None)
    assert_type(groups.prefetch_related(prefetch), QuerySet[Group])
    assert_type(perms.prefetch_related("content_type"), QuerySet[Permission])
    assert_type(groups.prefetch_related(None), QuerySet[Group])
    assert_type(Group.objects.prefetch_related(prefetch), QuerySet[Group])
    groups.prefetch_related(1)  # type: ignore[call-overload]  # pyright: ignore[reportCallIssue, reportArgumentType]  # pyrefly: ignore[no-matching-overload]  # ty: ignore[no-matching-overload]
    groups.prefetch_related(None, "permissions")  # type: ignore[call-overload]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-argument-type]
```

### [#425](https://github.com/sbdchd/django-types/pull/425) Stop modelling managers as QuerySet subclasses

add: tests/assert_type/db/models/test_managers.py

```python
def managers_are_not_querysets(manager: models.Manager[OtherModel]) -> None:
    len(manager)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-argument-type]
    manager[0]  # type: ignore[index]  # pyright: ignore[reportIndexIssue]  # pyrefly: ignore[bad-index]  # ty: ignore[not-subscriptable]
    manager.delete()  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # pyrefly: ignore[missing-attribute]  # ty: ignore[unresolved-attribute]
```

### [#421](https://github.com/sbdchd/django-types/pull/421) fix(typing): preserve queryset type in as_manager

add: tests/assert_type/db/models/test_managers.py

```python
assert_type(OtherQuerySet.as_manager().filter(), OtherQuerySet)
assert_type(OtherQuerySet.as_manager().get(), OtherModel)
```

### [#420](https://github.com/sbdchd/django-types/pull/420) Type BaseDatabaseWrapper.execute_wrapper and constraint_checks_disabled as context managers

add: tests/assert_type/db/test_connection.py

```python
from collections.abc import Callable
from typing import Any

from django.db import connection
from typing_extensions import assert_type


def blocker(
    execute: Callable[[str, Any, bool, dict[str, Any]], Any], sql: str, params: Any, many: bool, context: dict[str, Any]
) -> Any:
    return execute(sql, params, many, context)


with connection.execute_wrapper(blocker) as entered:
    assert_type(entered, None)
with connection.constraint_checks_disabled() as disabled:
    assert_type(disabled, None)
```

### [#416](https://github.com/sbdchd/django-types/pull/416) type manager chain calls as returning the manager's queryset

add: tests/assert_type/db/models/test_managers.py

```python
def manager_chain_methods_return_its_queryset(manager: models.Manager[OtherModel, OtherQuerySet]) -> None:
    assert_type(manager.get_queryset(), OtherQuerySet)
    assert_type(manager.filter().order_by("pk"), OtherQuerySet)
    assert_type(manager.union(manager.all()), OtherQuerySet)
    assert_type(manager.get(), OtherModel)
    plain: models.Manager[OtherModel] = manager
    assert_type(plain.filter(), QuerySet[OtherModel])
```

### [#414](https://github.com/sbdchd/django-types/pull/414) type admin action callables as returning HttpResponseBase | None

add: tests/assert_type/contrib/admin/test_options.py

```python
import sys

if sys.version_info >= (3, 12):

    class OverrideActionsAdmin(admin.ModelAdmin[ValidActionModel]):
        @admin.action(description="Archive")
        def archive(self, request: HttpRequest, queryset: QuerySet[ValidActionModel]) -> None: ...

        @override
        def get_actions(
            self, request: HttpRequest, action_location: admin.ActionLocation = admin.ActionLocation.CHANGE_LIST
        ) -> dict[str, admin.Action]:
            actions = super().get_actions(request, action_location)
            actions["archive"] = admin.Action(
                func=OverrideActionsAdmin.archive,
                name="archive",
                description="Archive",
                plural_description="Archive",
                locations=[action_location],
            )
            return actions
```

### [#407](https://github.com/sbdchd/django-types/pull/407) fix field descriptor types that force casts or dead guards

add: tests/assert_type/db/models/fields/test_lazy_reference/models.py

```python
from __future__ import annotations

from typing import Any, assert_type

from django.db import models


class Author(models.Model): ...


class Book(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE, null=True)
    data = models.JSONField()


def unresolved_field_type_vars_default_to_any(book: Book) -> None:
    # only the mypy plugin resolves the string reference, other checkers fall back to the `Any` default
    assert_type(book.author, Author | None)  # pyright: ignore[reportAssertTypeFailure]  # pyrefly: ignore[assert-type]  # ty: ignore[type-assertion-failure]
    assert_type(book.data, Any)
```

### [#405](https://github.com/sbdchd/django-types/pull/405) add symbols Django exports but the stubs omit

add: tests/assert_type/contrib/admin/test_sites.py

```python
from typing import assert_type

from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import site
from django.contrib.auth.models import User

assert_type(site.get_model_admin(User), ModelAdmin[User])
```

### [#397](https://github.com/sbdchd/django-types/pull/397) Improve `django-stubs/test/client.pyi`

add: tests/assert_type/test/test_client.py

```python
from django.http import HttpRequest, HttpResponse
from django.test.client import conditional_content_removal

assert_type(client.check_exception(response), None)
assert_type(conditional_content_removal(HttpRequest(), HttpResponse()), HttpResponse)
```

### [#376](https://github.com/sbdchd/django-types/pull/376) sync StrOrPromise with django-stubs

add: tests/assert_type/utils/test_text.py

```python
from typing_extensions import assert_type

from django.utils.functional import _StrPromise
from django.utils.text import slugify
from django.utils.translation import gettext_lazy


def test_slugify(value: str) -> None:
    assert_type(slugify(value), str)
    assert_type(slugify(gettext_lazy("Hello World")), _StrPromise)
```

### [#362](https://github.com/sbdchd/django-types/pull/362) Improve `django.core.management` types

add: tests/assert_type/core/management/test_base.py

```python
from typing import NoReturn

from django.core.management.base import CommandParser


def _error(parser: CommandParser) -> NoReturn:
    parser.error("boom")
```

### [#350](https://github.com/sbdchd/django-types/pull/350) refactor: Update dispatcher typing

add: tests/assert_type/dispatch/test_dispatcher.py

```python
from django.dispatch import Signal, receiver
from typing_extensions import assert_type

sig = Signal()


@receiver([sig, sig], sender=object, dispatch_uid="uid")
def handler(sender: object, **kwargs: object) -> int:
    return 1


assert_type(handler(object()), int)
```

### [#337](https://github.com/sbdchd/django-types/pull/337) fix: Exists(...) | Q(...)

add: tests/assert_type/db/models/test_expressions.py

```python
from typing import cast

from django.db.models import Exists, Model, Q, QuerySet
from typing_extensions import assert_type

queryset = cast("QuerySet[Model]", object())
assert_type(Exists(queryset) | Q(pk=1), Q)
assert_type(Exists(queryset) & Q(pk=1), Q)
assert_type(Exists(queryset) ^ Q(pk=1), Q)
```

### [#330](https://github.com/sbdchd/django-types/pull/330) fix: Preserve signature for keep_lazy_text

add: tests/assert_type/utils/test_functional.py

```python
from django.utils.functional import keep_lazy_text
from django.utils.html import format_html
from django.utils.safestring import SafeString
from typing_extensions import assert_type

format_html_lazy = keep_lazy_text(format_html)
assert_type(format_html_lazy("<b>{}</b>", "x"), SafeString)
```

### [#316](https://github.com/sbdchd/django-types/pull/316) Add django-stub for Composite Primary Key 

add: tests/assert_type/db/models/fields/test_composite_pk/models.py

```python
from __future__ import annotations

from typing import Any, assert_type

from django.db import models


class Release(models.Model):
    pk = models.CompositePrimaryKey("version", "name")
    version = models.IntegerField()
    name = models.CharField(max_length=20)


def composite_pk_reads_as_tuple(release: Release) -> None:
    assert_type(release.pk, tuple[Any, ...])
    release.pk = (1, "a")
    release.pk = None
```

### [#310](https://github.com/sbdchd/django-types/pull/310) Django 5.2, Python 3.10, update `django.contrib.admin.models`

add: tests/assert_type/contrib/admin/test_models.py

```python
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth.models import Group
from typing_extensions import assert_type


def log(user_id: int, groups: list[Group]) -> None:
    assert_type(LogEntry.objects.log_actions(user_id, groups, CHANGE), list[LogEntry])
    assert_type(LogEntry.objects.log_actions(user_id, groups, CHANGE, single_object=True), LogEntry)
```

### [#308](https://github.com/sbdchd/django-types/pull/308) contrib.admin.decorators: use TypeVar

add: tests/assert_type/contrib/admin/test_decorators.py

```python
from typing_extensions import assert_type

class SubDisplayModelAdmin(DisplayModelAdmin): ...

assert_type(admin.register(DisplayModel)(SubDisplayModelAdmin), type[SubDisplayModelAdmin])
```

### [#288](https://github.com/sbdchd/django-types/pull/288) fix some formset types (#271)

add: tests/assert_type/forms/test_formsets.py

```python
from django.forms import Form
from django.forms.formsets import BaseFormSet, formset_factory
from typing_extensions import assert_type


class ContactForm(Form): ...


ContactFormSet = formset_factory(ContactForm)
assert_type(ContactFormSet, type[BaseFormSet[ContactForm]])
assert_type(ContactFormSet().forms, list[ContactForm])
```

### [#271](https://github.com/sbdchd/django-types/pull/271) forms/formsets: Improve types

add: tests/assert_type/forms/test_formsets.py

```python
from django.forms.utils import ErrorDict


def test_errors(formset: BaseFormSet[Form]) -> None:
    assert_type(formset.errors, list[ErrorDict])
```

### [#268](https://github.com/sbdchd/django-types/pull/268) Update transaction.pyi

add: tests/assert_type/db/test_transaction.py

```python
from contextlib import AbstractContextManager

from django.db.transaction import atomic

cm: AbstractContextManager[None, None] = atomic()
```

### [#262](https://github.com/sbdchd/django-types/pull/262) Fix aiterator() signature.

add: tests/assert_type/db/models/test_queryset_row_type/models.py

```python
from collections.abc import AsyncIterator


async def aiterator_yields_the_row_type(qs: QuerySet[Blog], manager: models.Manager[Blog]) -> None:
    assert_type(qs.aiterator(), AsyncIterator[Blog])
    assert_type(manager.aiterator(), AsyncIterator[Blog])
    async for blog in qs.aiterator():
        assert_type(blog, Blog)
```

### [#258](https://github.com/sbdchd/django-types/pull/258) Improve types around template rendering

add: tests/assert_type/forms/test_renderers.py

```python
from typing import assert_type

from django.forms.renderers import DjangoTemplates, Jinja2, TemplatesSetting
from django.template.backends.base import _EngineTemplate
from django.template.backends.django import Template as DjangoTemplate
from django.template.backends.jinja2 import Template as Jinja2Template
from django.utils.safestring import SafeString

assert_type(DjangoTemplates().get_template("a.html"), DjangoTemplate)
assert_type(Jinja2().get_template("a.html"), Jinja2Template)
assert_type(TemplatesSetting().get_template("a.html"), _EngineTemplate)
assert_type(DjangoTemplates().get_template("a.html").render({}), SafeString)
```

### [#257](https://github.com/sbdchd/django-types/pull/257) contrib/admin/options: improve types

add: tests/assert_type/contrib/admin/test_options.py

```python
from typing_extensions import assert_type

def check_save_form(
    model_admin: admin.ModelAdmin[FullAdminModel], request: HttpRequest, form: FullAdminModelForm
) -> None:
    assert_type(model_admin.save_form(request, form, True), FullAdminModel)
```

### [#246](https://github.com/sbdchd/django-types/pull/246) Improvements to `django.contrib.auth`

add: tests/assert_type/contrib/auth/test_user_flags/models.py

```python
def user_or_anonymous_user_methods(user: User | AnonymousUser) -> None:
    assert_type(user.check_password("x"), bool)
    assert_type(user.get_group_permissions(), set[str])
```

### [#238](https://github.com/sbdchd/django-types/pull/238) `django.utils.deconstruct`: Improve types

add: tests/assert_type/utils/test_deconstruct.py

```python
from django.utils.deconstruct import deconstructible
from typing_extensions import assert_type


@deconstructible
class Bare:
    def __init__(self, x: int) -> None: ...


@deconstructible(path="app.WithPath")
class WithPath:
    def __init__(self, x: int) -> None: ...


assert_type(Bare(1), Bare)
assert_type(WithPath(1), WithPath)
```

### [#213](https://github.com/sbdchd/django-types/pull/213) django/test/utils.py polish

add: tests/assert_type/test/test_utils.py

```python
from django.test import SimpleTestCase


class MyTests(SimpleTestCase): ...


assert_type(override_settings(FOO="bar").decorate_class(MyTests), type[MyTests])
```

### [#210](https://github.com/sbdchd/django-types/pull/210) Improve `django.template`

add: tests/assert_type/template/test_loader.py

```python
from typing import assert_type

from django.template.backends.base import _EngineTemplate
from django.template.loader import get_template, select_template

assert_type(get_template("a.html"), _EngineTemplate)
assert_type(select_template(["a.html", "b.html"]), _EngineTemplate)
```

### [#208](https://github.com/sbdchd/django-types/pull/208) Improve `django.http` types

add: tests/assert_type/http/test_request.py

```python
from django.http import HttpRequest

request = HttpRequest()
assert_type(request.get_signed_cookie("k"), str)
assert_type(request.get_signed_cookie("k", None), str | None)
assert_type(request.get_signed_cookie("k", default=0, salt="s"), str | int)
```

### [#190](https://github.com/sbdchd/django-types/pull/190) Make managers in `django.contrib` generic

add: tests/assert_type/contrib/auth/test_models.py

```python
from django.contrib.auth.models import Group, GroupManager


class ProxyGroup(Group):
    class Meta:
        proxy = True
        app_label = "myapp"


assert_type(ProxyGroup.objects, GroupManager[ProxyGroup])
assert_type(ProxyGroup.objects.get_by_natural_key("admins"), ProxyGroup)
```

### [#189](https://github.com/sbdchd/django-types/pull/189) Add TransactionTestCase.assertQuerySetEqual

add: tests/assert_type/test/test_testcase.py

```python
from django.contrib.auth.models import User


class QuerySetEqualTestCase(TestCase):
    def test_transform_gets_the_row_type(self) -> None:
        users = User.objects.all()
        self.assertQuerySetEqual(users, ["admin"], transform=lambda u: u.username)
        self.assertQuerySetEqual(users.values_list("username"), [("admin",)], transform=tuple)
        self.assertQuerySetEqual(users.iterator(), ["admin"], transform=str)
        assert_type(self.assertQuerySetEqual(users, ["admin"]), None)
```

### [#159](https://github.com/sbdchd/django-types/pull/159) feat: support for Django 4.2

add: tests/assert_type/contrib/admin/views/test_decorators.py

```python
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from typing_extensions import assert_type


@staff_member_required
def bare(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


@staff_member_required(redirect_field_name="next", login_url="/login/")
def configured(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(bare(HttpRequest()), HttpResponse)
assert_type(configured(HttpRequest()), HttpResponse)
```

### [#131](https://github.com/sbdchd/django-types/pull/131) fix: Add `through` to ManyToManyField

add: tests/assert_type/db/models/fields/test_related_descriptors.py

```python
class Tag(models.Model):
    pass


class Post(models.Model):
    tags = models.ManyToManyField(Tag, through="Tagging")


class Tagging(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Article(models.Model):
    tags = models.ManyToManyField(Tag, through=Tagging)


assert_type(Article.tags.through, type[Tagging])  # pyrefly: ignore[assert-type]
```

### [#120](https://github.com/sbdchd/django-types/pull/120) feat: Add typings for async interface released for Django 4.1

add: tests/assert_type/db/models/test_queryset_row_type/models.py

```python
async def async_queryset_methods_keep_the_row_type(qs: QuerySet[Blog]) -> None:
    assert_type(await qs.aget(id=1), Blog)
    assert_type(await qs.afirst(), Blog | None)
    assert_type(await qs.acreate(), Blog)
    async for blog in qs:
        assert_type(blog, Blog)
    async for blog in qs.aiterator():
        assert_type(blog, Blog)
```

### [#119](https://github.com/sbdchd/django-types/pull/119) Allow `Any` in upload_to callback

add: tests/assert_type/db/models/fields/test_files.py

```python
same test as PR 105 (upload_path(instance: Upload, filename: str) accepted)
```

### [#105](https://github.com/sbdchd/django-types/pull/105) Set correct types if `upload_to` is a function

add: tests/assert_type/db/models/fields/test_files.py

```python
class Upload(models.Model):
    pass


def upload_path(instance: Upload, filename: str) -> str:
    return f"uploads/{instance.pk}/{filename}"


def no_args() -> str:
    return "uploads/"


class WithUploadTo(models.Model):
    file = models.FileField(upload_to=upload_path)
    image = models.ImageField(upload_to=upload_path)
    wrong = models.FileField(upload_to=no_args)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]  # pyrefly: ignore[bad-argument-type]  # ty: ignore[invalid-argument-type]
```

### [#64](https://github.com/sbdchd/django-types/pull/64) Improve typing on JSONField

add: tests/assert_type/db/models/fields/test_json.py

```python
from django.db import models
from typing_extensions import assert_type


class Doc(models.Model):
    data = models.JSONField[dict[str, list[int]], dict[str, list[int]]]()


def explicit_type_args_type_the_json_value(doc: Doc) -> None:
    assert_type(doc.data, dict[str, list[int]])  # pyrefly: ignore[assert-type]
```

### [#54](https://github.com/sbdchd/django-types/pull/54) Improve objects inside Model

add: tests/assert_type/db/models/test_base.py

```python
assert_type(MyModel._meta.model, type[MyModel])
```

### [#42](https://github.com/sbdchd/django-types/pull/42) fix(django): contrib.auth.models.User.objects, Manager -> UserManager

add: tests/assert_type/contrib/auth/test_models.py

```python
from django.contrib.auth.models import User, UserManager

assert_type(User.objects, UserManager[User])
assert_type(User.objects.create_superuser("admin"), User)
```

### [#37](https://github.com/sbdchd/django-types/pull/37) Add stubs for new admin decorators

add: tests/assert_type/contrib/admin/test_decorators.py

```python
from typing_extensions import assert_type

def check_decorators_keep_signature(request: HttpRequest, queryset: QuerySet[ActionModel]) -> None:
    model_admin = ActionModelAdmin(ActionModel, admin.site)
    assert_type(freestanding_action_http_response(model_admin, request, queryset), HttpResponse)
    assert_type(model_admin.method_action_file_response(request, queryset), FileResponse)
    assert_type(DisplayModelAdmin(DisplayModel, admin.site).admin_display_fancy(DisplayModel()), bool)
```

### [#10](https://github.com/sbdchd/django-types/pull/10) add(django): type csrf and vary decorators

add: tests/assert_type/views/test_decorators.py

```python
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, requires_csrf_token
from django.views.decorators.gzip import gzip_page
from django.views.decorators.http import require_POST
from typing_extensions import assert_type


@csrf_protect
def protected(request: HttpRequest, pk: int) -> HttpResponse:
    raise NotImplementedError


@ensure_csrf_cookie
@requires_csrf_token
@require_POST
@gzip_page
def with_cookie(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(protected(HttpRequest(), 1), HttpResponse)
assert_type(with_cookie(HttpRequest()), HttpResponse)
```

### [#8](https://github.com/sbdchd/django-types/pull/8) add(django): type more decorators

add: tests/assert_type/views/test_decorators.py

```python
from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.http import last_modified
from typing_extensions import assert_type


def latest(request: HttpRequest) -> datetime | None:
    raise NotImplementedError


@cache_page(60)
@last_modified(latest)
def cached(request: HttpRequest, pk: int) -> HttpResponse:
    raise NotImplementedError


@never_cache
def uncached(request: HttpRequest) -> HttpResponse:
    raise NotImplementedError


assert_type(cached(HttpRequest(), 1), HttpResponse)
assert_type(uncached(HttpRequest()), HttpResponse)
```

### [#2](https://github.com/sbdchd/django-types/pull/2) fix(django): add missing generic types params

add: tests/assert_type/http/test_request.py

```python
from django.http import HttpRequest
from typing_extensions import assert_type


def check_headers(request: HttpRequest) -> None:
    assert_type(request.headers.get("X-Foo"), str | None)
    assert_type(request.headers["X-Foo"], str)
```


## Tooling-only PRs (n/a)

- [#374](https://github.com/sbdchd/django-types/pull/374) release: 0.24.0
- [#371](https://github.com/sbdchd/django-types/pull/371) release: 0.23.0
- [#349](https://github.com/sbdchd/django-types/pull/349) Add pre commit hooks
- [#339](https://github.com/sbdchd/django-types/pull/339) typecheck tests with ty
- [#318](https://github.com/sbdchd/django-types/pull/318) release: 0.22.0
- [#317](https://github.com/sbdchd/django-types/pull/317) release: 0.21.0
- [#301](https://github.com/sbdchd/django-types/pull/301) Fix link to `django_stubs_ext` in README.md
- [#287](https://github.com/sbdchd/django-types/pull/287) chore: Replace poetry.dev-dependencies with poetry.group.dev.dependencies
- [#277](https://github.com/sbdchd/django-types/pull/277) bump version
- [#204](https://github.com/sbdchd/django-types/pull/204) document publishing
- [#203](https://github.com/sbdchd/django-types/pull/203) install dependencies for bump_version workflow
- [#202](https://github.com/sbdchd/django-types/pull/202) bump version with github actions
- [#195](https://github.com/sbdchd/django-types/pull/195) release: 0.18.0
- [#188](https://github.com/sbdchd/django-types/pull/188) Unify config files
- [#179](https://github.com/sbdchd/django-types/pull/179) docs: Use django-stubs-ext instead of manual patching
- [#178](https://github.com/sbdchd/django-types/pull/178) chore: Cleanup lint script
- [#160](https://github.com/sbdchd/django-types/pull/160) ci: replace circle with github actions
- [#152](https://github.com/sbdchd/django-types/pull/152) release: 0.17.0
- [#135](https://github.com/sbdchd/django-types/pull/135) Add py.typed files to django and psycopg2 stubs folders - pylance
- [#128](https://github.com/sbdchd/django-types/pull/128) Fix some spelling errors in the README
- [#122](https://github.com/sbdchd/django-types/pull/122) support m1 macs
- [#121](https://github.com/sbdchd/django-types/pull/121) release: 0.16.0
- [#113](https://github.com/sbdchd/django-types/pull/113) ForeignKey monkeypatch not needed for Django 4.1+
- [#107](https://github.com/sbdchd/django-types/pull/107) Documentation for annotations on related_name
- [#106](https://github.com/sbdchd/django-types/pull/106) release: 0.15.0
- [#103](https://github.com/sbdchd/django-types/pull/103) release: 0.14.1
- [#100](https://github.com/sbdchd/django-types/pull/100) release: 0.14.0
- [#92](https://github.com/sbdchd/django-types/pull/92) release: 0.13.0
- [#81](https://github.com/sbdchd/django-types/pull/81) release: 0.12.0
- [#78](https://github.com/sbdchd/django-types/pull/78) Fix typo and Django version requirements in Readme
- [#72](https://github.com/sbdchd/django-types/pull/72) #71 add type hint for id field
- [#70](https://github.com/sbdchd/django-types/pull/70) release: 0.10.0
- [#68](https://github.com/sbdchd/django-types/pull/68) release: 0.9.1
- [#61](https://github.com/sbdchd/django-types/pull/61) release: 0.9.0
- [#56](https://github.com/sbdchd/django-types/pull/56) ref(ci): update poetry to non-ancient version
- [#50](https://github.com/sbdchd/django-types/pull/50) release: 0.8.1
- [#48](https://github.com/sbdchd/django-types/pull/48) release: 0.8.0
- [#45](https://github.com/sbdchd/django-types/pull/45) Improve README.md
- [#43](https://github.com/sbdchd/django-types/pull/43) release: 0.7.0
- [#39](https://github.com/sbdchd/django-types/pull/39) release: 0.6.1
- [#33](https://github.com/sbdchd/django-types/pull/33) release: 0.6.1
- [#31](https://github.com/sbdchd/django-types/pull/31) release: 0.6.0
- [#24](https://github.com/sbdchd/django-types/pull/24) fix(pyscopg2): sql module Composable param type
- [#23](https://github.com/sbdchd/django-types/pull/23) release: 0.5.3
- [#22](https://github.com/sbdchd/django-types/pull/22) add(psycopg2): types for sql module
- [#21](https://github.com/sbdchd/django-types/pull/21) add(psycopg2): types for extras module
- [#19](https://github.com/sbdchd/django-types/pull/19) release 0.5.2
- [#17](https://github.com/sbdchd/django-types/pull/17) fix link to django-stubs-ext in readme
- [#16](https://github.com/sbdchd/django-types/pull/16) release: 0.5.1
- [#13](https://github.com/sbdchd/django-types/pull/13) add: orm example & ignore system links from search
- [#11](https://github.com/sbdchd/django-types/pull/11) add pyright
- [#9](https://github.com/sbdchd/django-types/pull/9) release: 0.5.0
- [#7](https://github.com/sbdchd/django-types/pull/7) release: 0.4.2
- [#6](https://github.com/sbdchd/django-types/pull/6) add(docs): related projects
- [#5](https://github.com/sbdchd/django-types/pull/5) add(ci): kodiak
