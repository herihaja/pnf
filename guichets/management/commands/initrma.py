# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from guichets.models import Guichet, Rma
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):

    def handle(self, *args, **options):
        ''' Selectionner tous les guichets actif et initialiser pour la periode en cours
        '''
        prev_month = date.today() + relativedelta(months=-1)
        prev_month = "%s-%s-01" % (prev_month.year, prev_month.month,)
        prev_month = datetime.strptime(prev_month, '%Y-%m-%d').date()

        guichets = Guichet.objects.filter(etat=1)
        for guichet in guichets:
            Rma.objects.get_or_create(guichet = guichet, periode = prev_month,
                              defaults={'agf': ''})

