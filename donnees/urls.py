# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from donnees.views import lister_donnees, ajouter_donnees, editer_donnees, supprimer_donnees, lister_cumuls, ajax_donnees, ajax_cumuls

urlpatterns = patterns('',
                        (r'^donnees/$', lister_donnees),
                        (r'^donnees/ajout/$', ajouter_donnees),
                        (r'^donnees/ajax/$', ajax_donnees),
                        (r'^donnees/editer/(?P<donnee_id>.+?)$', editer_donnees),
                        (r'^donnees/supprimer/(?P<donnee_id>.+?)$', supprimer_donnees),
                        (r'^cumuls/$', lister_cumuls),
                        (r'^cumuls/ajax/$', ajax_cumuls),
                    )
