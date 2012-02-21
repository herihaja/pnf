# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from compteur.views import index, ajoute_credit, edit_compteur

urlpatterns = patterns('',
                        (r'^compteur/$', index),
                        (r'^compteur/recharger/(?P<compteur_id>.+?)$', ajoute_credit),
                        (r'^compteur/ajuster/(?P<compteur_id>.+?)$', edit_compteur),
                    )
