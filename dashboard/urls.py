# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from dashboard.views import index_dashboard


urlpatterns = patterns('',
                        (r'^tableau-de-bord/$', index_dashboard),
                    )
