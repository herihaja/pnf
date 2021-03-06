# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from guichets.views import lister_guichet, ajouter_guichet, editer_guichet, \
    supprimer_guichet, ajax_guichet, ajax_bailleur, lister_bailleurs, \
    export_guichet, export_guichet_bailleurs, lister_envoi_rma, ajax_envoi_rma, export_envoi_rma

urlpatterns = patterns('',
                        (r'^guichets/$', lister_guichet),
                        (r'^guichets/ajout/$', ajouter_guichet),
                        (r'^guichets/export/(?P<filetype>.+?)/', export_guichet),
                        (r'^guichets/bailleurs/$', lister_bailleurs),
                        (r'^guichets/bailleurs/export/(?P<filetype>.+?)/', export_guichet_bailleurs),
                        (r'^guichets/editer/(?P<guichet_id>.+?)$', editer_guichet),
                        (r'^guichets/supprimer/(?P<guichet_id>.+?)$', supprimer_guichet),
                        (r'^guichets/ajax/$', ajax_guichet),
                        (r'^guichets/bailleurs/ajax/$', ajax_bailleur),
                        (r'^rma/envoi/$', lister_envoi_rma),
                        (r'^rma/envoi/ajax/$', ajax_envoi_rma),
                        (r'^rma/envoi/export/(?P<filetype>.+?)/$', export_envoi_rma),
                    )
