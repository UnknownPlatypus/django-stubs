from __future__ import annotations

from typing import TYPE_CHECKING

from mypy.nodes import Decorator, MemberExpr, Var
from mypy.types import AnyType, CallableType, TypeOfAny
from mypy.types import Type as MypyType

from mypy_django_plugin.lib import helpers

if TYPE_CHECKING:
    from mypy.plugin import AttributeContext

    from mypy_django_plugin.config import DjangoPluginConfig
    from mypy_django_plugin.django.context import DjangoContext


def get_type_of_settings_attribute(
    ctx: AttributeContext, django_context: DjangoContext, plugin_config: DjangoPluginConfig
) -> MypyType:
    if not isinstance(ctx.context, MemberExpr):
        return ctx.default_attr_type

    setting_name = ctx.context.name

    typechecker_api = helpers.get_typechecker_api(ctx)

    # When django-configurations is used, settings are declared as attributes of a
    # `Configuration` class that its importer materializes as the settings module
    # contents, overriding module-level names. So look the setting up on that class
    # and its bases first. Only uppercase attributes become settings at runtime.
    if plugin_config.django_configuration is not None and setting_name.isupper():
        settings_class_info = helpers.lookup_fully_qualified_typeinfo(
            typechecker_api, f"{django_context.django_settings_module}.{plugin_config.django_configuration}"
        )
        if settings_class_info is not None:
            for class_info in settings_class_info.mro[:-1]:  # `object` holds no settings
                sym = class_info.names.get(setting_name)
                if sym is None:
                    continue
                if isinstance(sym.node, Var):
                    attr_type = sym.type
                elif isinstance(sym.node, Decorator) and sym.node.var.is_property:
                    # The importer evaluates properties when settings load, so the
                    # setting carries the getter's return type.
                    func_type = sym.node.func.type
                    attr_type = func_type.ret_type if isinstance(func_type, CallableType) else None
                else:
                    # Methods, nested classes etc. are not materialized as settings
                    # in a statically visible way.
                    continue
                if attr_type is None:
                    # When analysing a function, mypy will defer analysis to a later pass
                    typechecker_api.handle_cannot_determine_type(setting_name, ctx.context)
                    return ctx.default_attr_type
                return attr_type

    # then look for the setting in the project settings file, then global settings
    settings_module = typechecker_api.modules.get(django_context.django_settings_module)
    global_settings_module = typechecker_api.modules.get("django.conf.global_settings")
    for module in [settings_module, global_settings_module]:
        if module is not None:
            sym = module.names.get(setting_name)
            if sym is not None:
                if sym.type is None:
                    # When analysing a function, mypy will defer analysis to a later pass
                    typechecker_api.handle_cannot_determine_type(setting_name, ctx.context)
                    return ctx.default_attr_type
                return sym.type

    # Now, we want to check if this setting really exist in runtime.
    # If it does, we just return `Any`, not to raise any false-positives.
    # But, we cannot reconstruct the exact runtime type.
    # See https://github.com/typeddjango/django-stubs/pull/1163
    if not plugin_config.strict_settings and hasattr(django_context.settings, setting_name):
        return AnyType(TypeOfAny.implementation_artifact)

    ctx.api.fail(f"'Settings' object has no attribute {setting_name!r}", ctx.context)
    return ctx.default_attr_type
