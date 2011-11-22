# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from sms.views import lister_reception, lister_envoi, sms_tester, ajax_reception, \
    ajax_envoi, export_envoi, export_reception, lister_communication, \
    ajax_communication, sms_broadcast, ajax_broadcast

urlpatterns = patterns('',
                        (r'^receptions/ajax/$', ajax_reception),
                        (r'^receptions/export/$', export_reception),
                        (r'^communications/list/$', lister_communication),
                        (r'^communications/ajax/$', ajax_communication),
                        (r'^receptions/(?P<statut>.+?)$', lister_reception),
                        (r'^receptions/$', lister_reception),
                        (r'^envois/$', lister_envoi),
                        (r'^envois/ajax/$', ajax_envoi),
                        (r'^envois/export/$', export_envoi),
                        (r'^smstester/$', sms_tester),
                        (r'^broadcast/$', sms_broadcast),
                        (r'^broadcast/ajax/$', ajax_broadcast),
                    )
