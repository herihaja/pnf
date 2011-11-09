# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from sms.views import lister_reception, lister_envoi, sms_tester, ajax_reception

urlpatterns = patterns('',
                        (r'^receptions/$', lister_reception),
                        (r'^receptions/ajax/$', ajax_reception),
                        (r'^envois/$', lister_envoi),
                        (r'^smstester/$', sms_tester),
                    )
