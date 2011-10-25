# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from bailleurs.views import lister_bailleur, ajouter_bailleur, editer_bailleur, supprimer_bailleur

urlpatterns = patterns('',
                        (r'^bailleurs/$', lister_bailleur),
                        (r'^bailleurs/ajout/$', ajouter_bailleur),
                        (r'^bailleurs/editer/(?P<bailleur_id>.+?)$', editer_bailleur),
                        (r'^bailleurs/supprimer/(?P<bailleur_id>.+?)$', supprimer_bailleur),
                    )