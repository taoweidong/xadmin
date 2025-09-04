#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : role
# author : ly_13
# date : 8/10/2024
import logging

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.core.fields import BasePrimaryKeyRelatedField
from common.core.serializers import BaseModelSerializer
from system.models import UserRole, Menu

logger = logging.getLogger(__name__)


class RoleSerializer(BaseModelSerializer):
    class Meta:
        model = UserRole
        fields = ['pk', 'name', 'code', 'is_active', 'description', 'menu', 'updated_time']
        table_fields = ['pk', 'name', 'code', 'is_active', 'description', 'updated_time']
        read_only_fields = ['pk']

    menu = BasePrimaryKeyRelatedField(queryset=Menu.objects, many=True, label=_("Menu"), attrs=['pk', 'name'],
                                      input_type="input")


class ListRoleSerializer(RoleSerializer):
    class Meta:
        model = UserRole
        fields = ['pk', 'name', 'is_active', 'code', 'menu', 'description', 'updated_time']
        read_only_fields = [x.name for x in UserRole._meta.fields]

    menu = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.ListField)
    def get_menu(self, instance):
        return []
