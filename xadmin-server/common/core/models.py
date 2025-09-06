#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : models
# author : ly_13
# date : 12/20/2023
import os
import time
import uuid

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.utils import get_logger

logger = get_logger(__name__)


class DbUuidModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("ID"))

    class Meta:
        abstract = True


class DbCharModel(models.Model):
    id = models.CharField(primary_key=True, max_length=128, verbose_name=_("ID"))

    class Meta:
        abstract = True


class AutoCleanFileMixin(object):
    """
    当对象包含文件字段，更新或者删除的时候，自动删除底层文件
    """

    def save(self, *args, **kwargs):
        if kwargs.get('force_insert', None):
            filelist = []
        else:
            filelist = self.__get_filelist(self._meta.model.objects.filter(pk=self.pk).first())
        result = super().save(*args, **kwargs)
        self.__delete_file(filelist, True)
        return result

    def delete(self, *args, **kwargs):
        filelist = self.__get_filelist()
        related_filelist = self.__get_related_filelist()
        result = super().delete(*args, **kwargs)
        self.__delete_file(filelist)
        self.__delete_related_files(related_filelist)
        return result

    def __delete_file(self, filelist, is_save=False):
        try:
            for item in filelist:
                if is_save:
                    file = getattr(self, item[0], None)
                    if file and file.name == item[1]:
                        continue
                item[2].name = item[1]
                item[2].delete(save=False)
        except Exception as e:
            logger.warning(f"remove {self} old file {filelist} failed, {e}")

    def __get_filelist(self, obj=None):
        filelist = []
        if obj is None:
            obj = self
        for field in obj._meta.fields:
            if isinstance(field, (models.ImageField, models.FileField)) and hasattr(obj, field.name):
                file_obj = getattr(obj, field.name, None)
                if file_obj:
                    filelist.append((field.name, file_obj.name, file_obj))
        return filelist

    def __get_related_filelist(self, obj=None):
        filelist = []
        if obj is None:
            obj = self
        for field in obj._meta.get_fields():
            if field.is_relation and field.related_model._meta.label == "system.UploadFile":
                file_data = getattr(obj, field.name, None)
                if isinstance(field, models.ManyToManyField):
                    file_data = file_data.all()
                if isinstance(file_data, (list, QuerySet)):
                    filelist.extend(file_data)
                else:
                    filelist.append(file_data)
        return filelist

    def __delete_related_files(self, filelist):
        for file in filelist:
            file.delete()

class DbBaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Created time"), null=True, blank=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name=_("Updated time"), null=True, blank=True)
    description = models.CharField(max_length=256, verbose_name=_("Description"), null=True, blank=True)

    class Meta:
        abstract = True


class DbAuditModel(DbBaseModel):
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True, blank=True,
                                verbose_name=_("Creator"), on_delete=models.SET_NULL, related_name='+')
    modifier = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='modifier_query', null=True,
                                 blank=True, verbose_name=_("Modifier"), on_delete=models.SET_NULL, related_name='+')
    dept_belong = models.ForeignKey(to="system.DeptInfo", related_query_name='dept_belong_query', null=True, blank=True,
                                    verbose_name=_("Data ownership department"), on_delete=models.SET_NULL,
                                    related_name='+')

    class Meta:
        abstract = True


def upload_directory_path(instance, filename):
    prefix = filename.split('.')[-1]
    tmp_name = f"{filename}_{time.time()}"
    new_filename = f"{uuid.uuid5(uuid.NAMESPACE_DNS, tmp_name).__str__().replace('-', '')}.{prefix}"
    labels = instance._meta.label_lower.split('.')
    if creator := getattr(instance, "creator", None):
        creator_pk = creator.pk
    else:
        creator_pk = 0
    return os.path.join(labels[0], labels[1], str(creator_pk), str(instance.pk if instance.pk else 0), new_filename)
