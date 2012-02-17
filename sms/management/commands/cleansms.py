# -*- coding: utf-8 -*-
from datetime import datetime
from django.core.management.base import BaseCommand
from sms.models import Reception

class Command(BaseCommand):

    def handle(self, *args, **options):
        ''' Suppression des doublons generes pas le demon gammu
        '''
        receptions = Reception.objects.filter(statut=2)

        prev = datetime.now()
        print "%s enregistrements" % (len(receptions),)
        for row in receptions:
            if prev-row.date_reception == 0:
                row.delete()
                print "deleting %s %s" % (row.date_reception, row.expediteur)
            else:
                prev = row.date_reception

