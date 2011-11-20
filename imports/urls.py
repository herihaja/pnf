# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from imports.views import importer_donnees, importer_localites, importer_bailleurs

urlpatterns = patterns('',
                        (r'^imports/donnees/$', importer_donnees),
                        (r'^imports/localites/$', importer_localites),
                        (r'^imports/guichets/$', importer_bailleurs),
                    )
