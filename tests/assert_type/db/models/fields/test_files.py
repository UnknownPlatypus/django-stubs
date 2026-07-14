from __future__ import annotations

from typing import assert_type

from django.core.files.storage import Storage
from django.db import models
from django.db.models.fields.files import FieldFile, FileDescriptor, ImageFieldFile, ImageFileDescriptor


class MyModel(models.Model):
    file = models.FileField()
    image = models.ImageField()

    null_file = models.FileField(null=True)
    null_image = models.ImageField(null=True)


instance = MyModel()
# At runtime, FileDescriptor.__get__ ALWAYS returns a FieldFile even when the underlying database value is NULL.
# It wraps None in FieldFile(instance, field, name=None).
# For ex:
# In [4]: Page.objects.get(video__isnull=False).video
# Out[4]: <FieldFile: video-1280x720_Pw9M7ro.webm>
#
# In [5]: Page.objects.get(video__isnull=True).video
# Out[5]: <FieldFile: None>

assert_type(instance.file, FieldFile)
assert_type(instance.image, ImageFieldFile)
assert_type(instance.null_file, FieldFile)
assert_type(instance.null_image, ImageFieldFile)


def image_field_accepts_file_field_kwargs() -> None:
    # ImageField forwards `upload_to`/`storage` to FileField at runtime, so both must type-check.
    class WithKwargs(models.Model):
        avatar = models.ImageField(upload_to="avatars/")
        cover = models.ImageField(upload_to="covers/", storage=Storage())

    instance = WithKwargs()
    assert_type(instance.avatar, ImageFieldFile)
    assert_type(instance.cover, ImageFieldFile)


def file_and_image_class_access_returns_specific_descriptor() -> None:
    # Class-level access returns the field's own descriptor object (matches runtime), not a generic
    # `_FieldDescriptor` wrapper that only exposes `.field`.
    class WithFiles(models.Model):
        doc = models.FileField()
        pic = models.ImageField()

    assert_type(WithFiles.doc, FileDescriptor)
    assert_type(WithFiles.pic, ImageFileDescriptor)
