#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : config
# author : ly_13
# date : 8/10/2024

import json
import logging

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.core.config import SysConfig, UserConfig
from common.core.fields import BasePrimaryKeyRelatedField
from common.core.serializers import BaseModelSerializer
from system.models import SystemConfig, UserPersonalConfig, UserInfo

logger = logging.getLogger(__name__)


class SystemConfigSerializer(BaseModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['pk', 'key', 'value', 'cache_value', 'is_active', 'inherit', 'access', 'description', 'created_time']
        read_only_fields = ['pk']
        fields_unexport = ['cache_value']  # 导入导出文件时，忽略该字段

    cache_value = serializers.SerializerMethodField(read_only=True, label=_("Config cache value"))

    @extend_schema_field(serializers.CharField)
    def get_cache_value(self, obj):
        val = SysConfig.get_value(obj.key)
        if isinstance(val, dict):
            return json.dumps(val)
        return json.dumps(val)


class UserPersonalConfigExportImportSerializer(SystemConfigSerializer):
    class Meta:
        model = UserPersonalConfig
        fields = ['pk', 'value', 'key', 'is_active', 'created_time', 'description', 'cache_value', 'owner', 'access']
        read_only_fields = ['pk']

    owner = BasePrimaryKeyRelatedField(attrs=['pk', 'username'], label=_("User"), queryset=UserInfo.objects,
                                       required=True)


class UserPersonalConfigSerializer(SystemConfigSerializer):
    class Meta:
        model = UserPersonalConfig
        fields = ['pk', 'config_user', 'owner', 'key', 'value', 'cache_value', 'is_active', 'access', 'description',
                  'created_time']

        read_only_fields = ['pk', 'owner']

    owner = BasePrimaryKeyRelatedField(attrs=['pk', 'username'], label=_("User"), read_only=True, format='{username}')
    config_user = BasePrimaryKeyRelatedField(write_only=True, many=True, queryset=UserInfo.objects,
                                             label=_("Users"), input_type='api-search-user')

    def create(self, validated_data):
        config_user = validated_data.pop('config_user', [])
        owner = validated_data.pop('owner', None)
        instance = None
        if not config_user and not owner:
            raise ValidationError(_("User cannot be null"))
        if owner:
            config_user.append(owner)
        for owner in config_user:
            validated_data['owner'] = owner
            instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('config_user', None)
        return super().update(instance, validated_data)

    @extend_schema_field(serializers.CharField)
    def get_cache_value(self, obj):
        val = UserConfig(obj.owner).get_value(obj.key)
        if isinstance(val, dict):
            val = json.dumps(val)
        return val
