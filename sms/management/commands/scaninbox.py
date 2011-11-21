# -*- coding: utf-8 -*-
from datetime import datetime
from sys import stderr, stdout
from django.core.management.base import BaseCommand, CommandError
from gammu.models import Inbox
from sms.views import process_sms, set_inbox_as_processed

class Command(BaseCommand):

    def handle(self, *args, **options):
        obj = Inbox.objects.filter(processed=False)
        n = 0
        for row in obj:
            # parser le message
            try:
                process_sms(row.sendernumber, row.textdecoded, row.receivingdatetime, row.recipientid)
            except:
                stderr.write('Error parsing message "%s"\n' % row.id)

            # marquer comme traite
            set_inbox_as_processed(row.id)
            n += 1

        # stdout.write('Traitement de %s messages a %s \n' % (n, datetime.now()))
