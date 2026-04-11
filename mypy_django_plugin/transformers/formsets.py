from __future__ import annotations

from typing import TYPE_CHECKING

from mypy.nodes import ARG_NAMED, ARG_POS, GDEF, PlaceholderNode, RefExpr, SymbolTableNode, TypeInfo
from mypy.types import AnyType, Instance, TypeOfAny

from mypy_django_plugin.lib import helpers

if TYPE_CHECKING:
    from mypy.nodes import CallExpr, Expression
    from mypy.plugin import DynamicClassDefContext

# Each factory maps to its base formset class and a list of (param_name, position)
# tuples describing how call arguments map to the base class type vars (in order).
#
# E.g. inlineformset_factory(parent_model, model, form=...) -> BaseInlineFormSet[_M, _ParentM, _ModelFormT]
#   type var _M      comes from arg "model" at position 1
#   type var _ParentM comes from arg "parent_model" at position 0
#   type var _ModelFormT comes from arg "form" at position 2
FACTORY_TO_BASE: dict[str, tuple[str, list[tuple[str, int]]]] = {
    "django.forms.formsets.formset_factory": (
        "django.forms.formsets.BaseFormSet",
        [("form", 0)],
    ),
    "django.forms.models.modelformset_factory": (
        "django.forms.models.BaseModelFormSet",
        [("model", 0), ("form", 1)],
    ),
    "django.forms.models.inlineformset_factory": (
        "django.forms.models.BaseInlineFormSet",
        [("model", 1), ("parent_model", 0), ("form", 2)],
    ),
}


def create_new_formset_class(ctx: DynamicClassDefContext) -> None:
    """
    Insert a new formset class node for factory calls like:
      '<Name> = formset_factory(<Form>)'
      '<Name> = inlineformset_factory(<ParentModel>, <Model>, ...)'

    This allows the returned class to be used as a base class for subclassing.
    """
    semanal_api = helpers.get_semanal_api(ctx)

    # Don't redeclare the formset class if we've already defined it.
    formset_sym = semanal_api.lookup_current_scope(ctx.name)
    if formset_sym and isinstance(formset_sym.node, TypeInfo):
        return

    callee = ctx.call.callee
    if not isinstance(callee, RefExpr) or not callee.fullname:
        return
    factory_config = FACTORY_TO_BASE.get(callee.fullname)
    if factory_config is None:
        return

    base_fullname, arg_specs = factory_config

    # Lookup the base formset TypeInfo
    base_sym = semanal_api.lookup_fully_qualified_or_none(base_fullname)
    if base_sym is None or not isinstance(base_sym.node, TypeInfo):
        if not ctx.api.final_iteration:
            if not (formset_sym and isinstance(formset_sym.node, PlaceholderNode)):
                ph = PlaceholderNode(ctx.api.qualified_name(ctx.name), ctx.call, ctx.call.line, becomes_typeinfo=True)
                ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, ph))
            ctx.api.defer()
        return

    base_formset_info = base_sym.node

    # Extract type args from call arguments, falling back to Any for missing ones
    type_args = [_resolve_type_arg(ctx.call, name, pos) for name, pos in arg_specs]
    # Pad with Any if the base class has more type vars than we extracted
    while len(type_args) < len(base_formset_info.type_vars):
        type_args.append(AnyType(TypeOfAny.special_form))

    base_instance = Instance(base_formset_info, type_args)

    new_info = helpers.create_type_info(ctx.name, semanal_api.cur_mod_id, bases=[base_instance])
    new_info.line = ctx.call.line
    new_info.defn.line = ctx.call.line

    ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, new_info, plugin_generated=True))


def _resolve_type_arg(call: CallExpr, name: str, position: int) -> Instance | AnyType:
    """Resolve a type argument from a call expression by parameter name or position."""
    arg = _get_argument(call, name, position)
    if isinstance(arg, RefExpr) and isinstance(arg.node, TypeInfo):
        return Instance(arg.node, [])
    return AnyType(TypeOfAny.special_form)


def _get_argument(call: CallExpr, name: str, position: int) -> Expression | None:
    """Extract an argument from a call expression by keyword name or positional index."""
    for arg, kind, arg_name in zip(call.args, call.arg_kinds, call.arg_names, strict=False):
        if kind == ARG_NAMED and arg_name == name:
            return arg

    pos_idx = 0
    for arg, kind, _ in zip(call.args, call.arg_kinds, call.arg_names, strict=False):
        if kind == ARG_POS:
            if pos_idx == position:
                return arg
            pos_idx += 1
    return None
