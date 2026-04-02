from __future__ import annotations

from typing import TYPE_CHECKING

from mypy.nodes import ARG_NAMED, ARG_POS, GDEF, PlaceholderNode, RefExpr, SymbolTableNode, TypeInfo
from mypy.types import AnyType, Instance, TypeOfAny

from mypy_django_plugin.lib import fullnames, helpers

if TYPE_CHECKING:
    from mypy.nodes import CallExpr, Expression
    from mypy.plugin import DynamicClassDefContext
    from mypy.semanal import SemanticAnalyzer


def _get_callee_fullname(call: CallExpr) -> str | None:
    """Get the fullname of the function being called."""
    callee = call.callee
    if isinstance(callee, RefExpr) and callee.fullname:
        return callee.fullname
    return None


def _get_argument(call: CallExpr, name: str, position: int) -> Expression | None:
    """Extract an argument from a call expression by name or position.

    Searches keyword arguments by name first, then falls back to positional.
    """
    # Check keyword arguments first
    for arg, kind, arg_name in zip(call.args, call.arg_kinds, call.arg_names, strict=False):
        if kind == ARG_NAMED and arg_name == name:
            return arg

    # Fall back to positional
    pos_idx = 0
    for arg, kind, _ in zip(call.args, call.arg_kinds, call.arg_names, strict=False):
        if kind == ARG_POS:
            if pos_idx == position:
                return arg
            pos_idx += 1

    return None


def _resolve_typeinfo_from_arg(arg: Expression | None) -> TypeInfo | None:
    """Resolve a TypeInfo from a call argument expression."""
    if isinstance(arg, RefExpr) and isinstance(arg.node, TypeInfo):
        return arg.node
    return None


def create_new_formset_class(ctx: DynamicClassDefContext) -> None:
    """
    Insert a new formset class node for:
      '<Name> = formset_factory(<Form>)'
      '<Name> = modelformset_factory(<Model>, ...)'
      '<Name> = inlineformset_factory(<ParentModel>, <Model>, ...)'

    This allows the returned class to be used as a base class for subclassing.
    """
    semanal_api = helpers.get_semanal_api(ctx)

    # Don't redeclare the formset class if we've already defined it.
    formset_sym = semanal_api.lookup_current_scope(ctx.name)
    if formset_sym and isinstance(formset_sym.node, TypeInfo):
        # This is just a deferral run where our work is already finished
        return

    new_formset_info = _create_formset_class_from_factory_call(semanal_api, ctx.call, ctx.name)
    if new_formset_info is None:
        if not ctx.api.final_iteration:
            if not (formset_sym and isinstance(formset_sym.node, PlaceholderNode)):
                ph = PlaceholderNode(ctx.api.qualified_name(ctx.name), ctx.call, ctx.call.line, becomes_typeinfo=True)
                ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, ph))
            ctx.api.defer()
        return


def _create_formset_class_from_factory_call(api: SemanticAnalyzer, call_expr: CallExpr, name: str) -> TypeInfo | None:
    """
    Create a new TypeInfo for a formset class from a factory call.

    Returns None if the call can't be resolved yet (triggers deferral).
    """
    callee_fullname = _get_callee_fullname(call_expr)
    if callee_fullname is None:
        return None

    base_fullname: str
    type_args: list[Instance | AnyType]

    if callee_fullname == fullnames.FORMSET_FACTORY_FULLNAME:
        base_fullname = fullnames.BASEFORMSET_CLASS_FULLNAME
        type_args = _extract_formset_factory_type_args(call_expr)
    elif callee_fullname == fullnames.MODELFORMSET_FACTORY_FULLNAME:
        base_fullname = fullnames.BASEMODELFORMSET_CLASS_FULLNAME
        type_args = _extract_modelformset_factory_type_args(call_expr)
    elif callee_fullname == fullnames.INLINEFORMSET_FACTORY_FULLNAME:
        base_fullname = fullnames.BASEINLINEFORMSET_CLASS_FULLNAME
        type_args = _extract_inlineformset_factory_type_args(call_expr)
    else:
        return None

    # Lookup the base formset TypeInfo
    base_sym = api.lookup_fully_qualified_or_none(base_fullname)
    if base_sym is None or not isinstance(base_sym.node, TypeInfo):
        return None
    base_formset_info = base_sym.node

    # Pad type_args with Any if we have fewer than the base class expects
    expected_tvars = len(base_formset_info.type_vars)
    while len(type_args) < expected_tvars:
        type_args.append(AnyType(TypeOfAny.special_form))

    # Create the parameterized base instance
    base_instance = Instance(base_formset_info, type_args)

    # Create a new TypeInfo for the dynamic formset class
    new_info = helpers.create_type_info(name, api.cur_mod_id, bases=[base_instance])
    new_info.line = call_expr.line
    new_info.defn.line = call_expr.line
    new_info.type_vars = base_formset_info.type_vars
    new_info.defn.type_vars = base_formset_info.defn.type_vars

    # Add the new formset class to the current module
    module = api.modules[api.cur_mod_id]
    module.names[name] = SymbolTableNode(GDEF, new_info, plugin_generated=True)
    return new_info


def _extract_formset_factory_type_args(call_expr: CallExpr) -> list[Instance | AnyType]:
    """Extract type args for formset_factory(form, ...) -> BaseFormSet[_F]."""
    # formset_factory(form: type[_F], ...) -> type[BaseFormSet[_F]]
    form_arg = _get_argument(call_expr, "form", 0)
    form_info = _resolve_typeinfo_from_arg(form_arg)
    if form_info is None:
        return [AnyType(TypeOfAny.special_form)]
    return [Instance(form_info, [])]


def _extract_modelformset_factory_type_args(call_expr: CallExpr) -> list[Instance | AnyType]:
    """Extract type args for modelformset_factory(model, ...) -> BaseModelFormSet[_M, _ModelFormT]."""
    # modelformset_factory(model: type[_M], form: type[_ModelFormT] = ...) -> type[BaseModelFormSet[_M, _ModelFormT]]
    model_arg = _get_argument(call_expr, "model", 0)
    model_info = _resolve_typeinfo_from_arg(model_arg)
    if model_info is None:
        return [AnyType(TypeOfAny.special_form), AnyType(TypeOfAny.special_form)]

    form_arg = _get_argument(call_expr, "form", 1)
    form_info = _resolve_typeinfo_from_arg(form_arg)
    form_type: Instance | AnyType = Instance(form_info, []) if form_info else AnyType(TypeOfAny.special_form)

    return [Instance(model_info, []), form_type]


def _extract_inlineformset_factory_type_args(call_expr: CallExpr) -> list[Instance | AnyType]:
    """Extract type args for inlineformset_factory(parent, model, ...) -> BaseInlineFormSet."""
    # inlineformset_factory(parent_model: type[_ParentM], model: type[_M], form: type[_ModelFormT] = ...)
    #   -> type[BaseInlineFormSet[_M, _ParentM, _ModelFormT]]
    parent_arg = _get_argument(call_expr, "parent_model", 0)
    parent_info = _resolve_typeinfo_from_arg(parent_arg)
    if parent_info is None:
        return [AnyType(TypeOfAny.special_form), AnyType(TypeOfAny.special_form), AnyType(TypeOfAny.special_form)]

    model_arg = _get_argument(call_expr, "model", 1)
    model_info = _resolve_typeinfo_from_arg(model_arg)
    if model_info is None:
        return [AnyType(TypeOfAny.special_form), AnyType(TypeOfAny.special_form), AnyType(TypeOfAny.special_form)]

    form_arg = _get_argument(call_expr, "form", 2)
    form_info = _resolve_typeinfo_from_arg(form_arg)
    form_type: Instance | AnyType = Instance(form_info, []) if form_info else AnyType(TypeOfAny.special_form)

    return [Instance(model_info, []), Instance(parent_info, []), form_type]
