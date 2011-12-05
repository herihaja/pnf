# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from plots.views import graph

urlpatterns = patterns('',
                        (r'^plots/$', graph),
                    )
