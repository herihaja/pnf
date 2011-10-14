# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from localites.views import editer_province, ajouter_province, lister_province, supprimer_province, \
    lister_region, editer_region, ajouter_region, supprimer_region,\
    lister_district, editer_district, ajouter_district, supprimer_district, \
    lister_commune, editer_commune, ajouter_commune, supprimer_commune

urlpatterns = patterns('',
                        (r'^localites/provinces/$', lister_province),
                        (r'^localites/provinces/ajout/$', ajouter_province),
                        (r'^localites/provinces/editer/(?P<province_id>.+?)$', editer_province),
                        (r'^localites/provinces/supprimer/(?P<province_id>.+?)$', supprimer_province),

                        (r'^localites/regions/$', lister_region),
                        (r'^localites/regions/ajout/$', ajouter_region),
                        (r'^localites/regions/editer/(?P<region_id>.+?)$', editer_region),
                        (r'^localites/regions/supprimer/(?P<region_id>.+?)$', supprimer_region),

                        (r'^localites/districts/$', lister_district),
                        (r'^localites/districts/ajout/$', ajouter_district),
                        (r'^localites/districts/editer/(?P<district_id>.+?)$', editer_district),
                        (r'^localites/districts/supprimer/(?P<district_id>.+?)$', supprimer_district),
                       
                        (r'^localites/communes/$', lister_commune),
                        (r'^localites/communes/ajout/$', ajouter_commune),
                        (r'^localites/communes/editer/(?P<commune_id>.+?)$', editer_commune),
                        (r'^localites/communes/supprimer/(?P<commune_id>.+?)$', supprimer_commune),
                    )
