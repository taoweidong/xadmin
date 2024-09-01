#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : tasks
# author : ly_13
# date : 7/30/2024

import os

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.utils.translation import gettext_lazy as _

logger = get_task_logger(__name__)


@shared_task(verbose_name=_("Send email"))
def send_mail_async(*args, **kwargs):
    """ Using celery to send email async

    You can use it as django send_mail function

    Example:
    send_mail_sync.delay(subject, message, from_mail, recipient_list, fail_silently=False, html_message=None)

    Also, you can ignore the from_mail, unlike django send_mail, from_email is not a required args:

    Example:
    send_mail_sync.delay(subject, message, recipient_list, fail_silently=False, html_message=None)
    """
    if len(args) == 3:
        args = list(args)
        args[0] = (settings.EMAIL_SUBJECT_PREFIX or '') + args[0]
        from_email = settings.EMAIL_FROM or settings.EMAIL_HOST_USER
        args.insert(2, from_email)

    args = tuple(args)
    try:
        return send_mail(connection=get_connection(), *args, **kwargs)
    except Exception as e:
        logger.error("Sending mail error: {}".format(e))


@shared_task(verbose_name=_("Send email attachment"))
def send_mail_attachment_async(subject, message, recipient_list, attachment_list=None):
    if attachment_list is None:
        attachment_list = []
    from_email = settings.EMAIL_FROM or settings.EMAIL_HOST_USER
    subject = (settings.EMAIL_SUBJECT_PREFIX or '') + subject
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
        connection=get_connection(),
    )
    for attachment in attachment_list:
        email.attach_file(attachment)
        os.remove(attachment)
    try:
        return email.send()
    except Exception as e:
        logger.error("Sending mail attachment error: {}".format(e))
