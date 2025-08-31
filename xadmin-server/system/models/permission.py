#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : permission
# author : ly_13
# date : 8/10/2024


from django.db import models
from django.utils.translation import gettext_lazy as _

from common.core.models import DbAuditModel, DbCharModel


class FieldPermission(DbAuditModel, DbCharModel):
    role = models.ForeignKey("system.UserRole", on_delete=models.CASCADE, verbose_name=_(
        "Role"))
    menu = models.ForeignKey("system.Menu", on_delete=models.CASCADE, verbose_name=_(
        "Menu"))
    field = models.ManyToManyField("system.ModelLabelField", verbose_name=_(
        "Field"), null=True, blank=True)

    class Meta:
        verbose_name = _("Field permission")
        verbose_name_plural = verbose_name
        ordering = ("-created_time",)
        unique_together = ("role", "menu")

    def save(self, *args, **kwargs):
        self.id = f"{self.role.pk}-{self.menu.pk}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk}-{self.role.name}-{self.created_time}"}]}}}
