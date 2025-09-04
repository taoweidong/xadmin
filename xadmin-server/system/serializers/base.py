#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : base
# author : ly_13
# date : 8/10/2024

import logging

from django.utils.translation import gettext_lazy as _

from common.core.fields import BasePrimaryKeyRelatedField, LabeledChoiceField
from common.core.serializers import BaseModelSerializer
from system.models import UserRole, ModeTypeAbstract

logger = logging.getLogger(__name__)


class BaseRoleRuleInfo(BaseModelSerializer):
    roles = BasePrimaryKeyRelatedField(queryset=UserRole.objects, allow_null=True, required=False, format="{name}",
                                       attrs=['pk', 'name', 'code'], label=_("Role permission"), many=True)
    mode_type = LabeledChoiceField(choices=ModeTypeAbstract.ModeChoices.choices, label=_("Mode type"),
                                   default=ModeTypeAbstract.ModeChoices.OR.value)