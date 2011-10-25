# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from imports.views import importer_donnees

urlpatterns = patterns('',
                        (r'^imports/$', importer_donnees),
                    )
