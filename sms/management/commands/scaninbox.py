# -*- coding: utf-8 -*-
from datetime import datetime
from sys import stderr, stdout
from django.core.management.base import BaseCommand, CommandError
from gammu.models import Inbox
from sms.views import cron_process_sms
import threading

class Command(BaseCommand):

    def handle(self, *args, **options):
        obj = Inbox.objects.filter(processed=False)
        for row in obj:
            try:
                cron_process_sms(row)
            except:
                pass
