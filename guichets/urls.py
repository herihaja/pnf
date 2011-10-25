# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from guichets.views import lister_guichet, ajouter_guichet, editer_guichet, supprimer_guichet

urlpatterns = patterns('',
                        (r'^guichets/$', lister_guichet),
                        (r'^guichets/ajout/$', ajouter_guichet),
                        (r'^guichets/editer/(?P<guichet_id>.+?)$', editer_guichet),
                        (r'^guichets/supprimer/(?P<guichet_id>.+?)$', supprimer_guichet),
                    )