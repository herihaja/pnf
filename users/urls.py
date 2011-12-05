# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
                        (r'^connexion/$', login),
                        (r'^deconnexion/$', logout),
                        (r'^utilisateurs/$', lister_user),
                        (r'^utilisateurs/supprimer/(?P<user_id>.+?)/$', supprimer_user),
                        (r'^utilisateurs/ajouter/$', ajouter_user),
                        (r'^utilisateurs/editer/(?P<user_id>.+?)/$', editer_user),
                        (r'^utilisateurs/ajax/$', ajax_user),
                    )
