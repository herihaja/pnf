from django.conf.urls.defaults import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
#                        (r'', include('pnf.bailleurs.urls')),
#                        (r'', include('pnf.donnees.urls')),
#                        (r'', include('pnf.guichets.urls')),
#                        (r'', include('pnf.indicateurs.urls')),
                        (r'', include('pnf.localites.urls')),
#                        (r'', include('pnf.ratios.urls')),
#                        (r'', include('pnf.sms.urls')),
#                        (r'', include('pnf.utilisateurs')),
                        url(r'^admin/', include(admin.site.urls)),
                        )
