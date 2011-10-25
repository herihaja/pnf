# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from sms.views import lister_reception, lister_envoi, editer_reception

urlpatterns = patterns('',
                        (r'^receptions/$', lister_reception),
                        (r'^envois/$', lister_envoi),
                        (r'^receptions/edit/(P<reception_id>.+?)$', editer_reception),
                    )
