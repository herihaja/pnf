# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from sms.views import nettoyer_reception

class Command(BaseCommand):

    def handle(self, *args, **options):
        nettoyer_reception()
