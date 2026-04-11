from __future__ import annotations

from typing import Any, override

from django.db import models
from django.forms import (
    BaseInlineFormSet,
    BaseModelFormSet,
    Form,
    formset_factory,
    inlineformset_factory,  # pyright: ignore[reportUnknownVariableType]
    modelformset_factory,  # pyright: ignore[reportUnknownVariableType]
)
from typing_extensions import assert_type


class Article(models.Model):
    class Meta:
        app_label = "assert_type"


class Category(models.Model):
    class Meta:
        app_label = "assert_type"


# formset_factory: subclassing

MyFormSet = formset_factory(Form)


class CustomFormSet(MyFormSet):
    @override
    def clean(self) -> None:
        super().clean()


custom_fs = CustomFormSet()
assert_type(custom_fs, CustomFormSet)


# modelformset_factory: subclassing

ArticleMFS: type[BaseModelFormSet[Article, Any]] = modelformset_factory(Article)


class CustomArticleMFS(ArticleMFS):
    @override
    def clean(self) -> None:
        super().clean()


custom_mfs = CustomArticleMFS()
assert_type(custom_mfs, CustomArticleMFS)


# inlineformset_factory: subclassing

ArticleFS: type[BaseInlineFormSet[Article, Category, Any]] = inlineformset_factory(Category, Article)


class CustomArticleFS(ArticleFS):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


custom_ifs = CustomArticleFS(instance=Category())
assert_type(custom_ifs, CustomArticleFS)
assert_type(custom_ifs.instance, Category)
