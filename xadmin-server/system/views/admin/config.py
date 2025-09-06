#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : server
# filename : config
# author : ly_13
# date : 6/16/2023
import logging

from django_filters import rest_framework as filters

from common.core.filter import BaseFilterSet, PkMultipleFilter
from common.core.modelset import BaseModelSet, ImportExportDataAction
from system.models import SystemConfig, UserPersonalConfig
from system.serializers.config import SystemConfigSerializer, UserPersonalConfigSerializer, \
    UserPersonalConfigExportImportSerializer
from system.utils.modelset import InvalidConfigCacheAction

logger = logging.getLogger(__name__)


class SystemConfigFilter(BaseFilterSet):
    pk = filters.UUIDFilter(field_name='id')
    key = filters.CharFilter(field_name='key', lookup_expr='icontains')
    value = filters.CharFilter(field_name='value', lookup_expr='icontains')

    class Meta:
        model = SystemConfig
        fields = ['pk', 'is_active', 'key', 'inherit', 'access', 'value', 'description']


class SystemConfigView(BaseModelSet, InvalidConfigCacheAction, ImportExportDataAction):
    """
    系统配置管理
    """
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    ordering_fields = ['created_time']
    filterset_class = SystemConfigFilter

    def get_queryset(self):
        # 优化查询
        return self.queryset


class UserPersonalConfigFilter(SystemConfigFilter):
    pk = filters.UUIDFilter(field_name='id')
    username = filters.CharFilter(field_name='owner__username')
    owner_id = PkMultipleFilter(input_type='api-search-user')

    class Meta:
        model = UserPersonalConfig
        fields = ['pk', 'is_active', 'key', 'access', 'username', 'owner_id', 'value', 'description']


class UserPersonalConfigView(BaseModelSet, InvalidConfigCacheAction, ImportExportDataAction):
    """
    用户配置管理
    """
    queryset = UserPersonalConfig.objects.all()
    serializer_class = UserPersonalConfigSerializer
    ordering_fields = ['created_time']
    filterset_class = UserPersonalConfigFilter
    import_data_serializer_class = UserPersonalConfigExportImportSerializer
    export_data_serializer_class = UserPersonalConfigExportImportSerializer

    def get_queryset(self):
        # 优化查询，使用select_related减少数据库查询
        if self.action == 'list':
            return self.queryset.select_related('owner')
        return self.queryset