from django.conf.urls.defaults import patterns, url
from pnf.localites.views import ajouter_province, lister_province


urlpatterns = patterns('',
                        (r'^localites/provinces/$', lister_province),
                        (r'^localites/provinces/ajout/$', ajouter_province),
                    )
