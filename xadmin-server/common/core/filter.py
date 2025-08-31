#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : server
# filename : filter
# author : ly_13
# date : 6/2/2023
import datetime
import logging

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from django_filters.fields import MultipleChoiceField
from rest_framework.exceptions import NotAuthenticated
from rest_framework.filters import BaseFilterBackend

from common.cache.storage import CommonResourceIDsCache

logger = logging.getLogger(__name__)


class OwnerUserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.user and request.user.is_authenticated:
            return queryset.filter(owner=request.user)
        raise NotAuthenticated("Unauthorized authentication")


class CreatorUserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.user and request.user.is_authenticated:
            return queryset.filter(creator=request.user)
        raise NotAuthenticated("Unauthorized authentication")


class BaseFilterSet(filters.FilterSet):
    pk = filters.NumberFilter(field_name='id')
    spm = filters.CharFilter(field_name='spm', method='get_spm_filter')
    creator = filters.NumberFilter(field_name='creator')
    modifier = filters.NumberFilter(field_name='modifier')
    created_time = filters.DateTimeFromToRangeFilter(field_name='created_time')
    updated_time = filters.DateTimeFromToRangeFilter(field_name='updated_time')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')

    def get_spm_filter(self, queryset, name, value):
        pks = CommonResourceIDsCache(value).get_storage_cache()
        if pks:
            return queryset.filter(pk__in=pks)
        return queryset


class PkMultipleChoiceField(MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages["required"], code="required")


class PkMultipleFilter(filters.MultipleChoiceFilter):
    """
    通过 input_type 来自定义前端展示类型
    """

    field_class = PkMultipleChoiceField

    def __init__(self, **kwargs):
        self.input_type = kwargs.pop('input_type', None)
        super().__init__(**kwargs)
