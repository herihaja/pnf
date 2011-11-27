# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from projets.views import lister_projet, ajouter_projet, export_projet, ajax_projet, editer_projet, supprimer_projet

urlpatterns = patterns('',
                        (r'^projets/$', lister_projet),
                        (r'^projets/ajout/$', ajouter_projet),
                        (r'^projets/export/$', export_projet),
                        (r'^projets/ajax/$', ajax_projet),
                        (r'^projets/editer/(?P<projet_id>.+?)$', editer_projet),
                        (r'^projets/supprimer/(?P<projet_id>.+?)$', supprimer_projet),
                    )
