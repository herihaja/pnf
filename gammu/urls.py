# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic import list_detail
from gammu.models import Inbox

inbox_dict = {
    'queryset': Inbox.objects.all(),
}


urlpatterns = patterns('',
                        (r'^inbox/$', list_detail.object_list, inbox_dict)
                    )
