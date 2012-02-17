# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
from sms.models import Reception

class Command(BaseCommand):

    def handle(self, *args, **options):
        ''' Suppression des doublons generes pas le demon gammu
        '''
        receptions = Reception.objects.filter(statut=2)

        prev = datetime.datetime.now()
        print "%s enregistrements" % (len(receptions),)
        for row in receptions:
            td = prev - row.date_reception
            if td == datetime.timedelta(0):
                row.delete()
            else:
                prev = row.date_reception

