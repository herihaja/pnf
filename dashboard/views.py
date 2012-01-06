# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from donnees.models import Donnees, Cumul
from helpers import process_datatables_posted_vars, query_datatables, export_excel
import simplejson
from datetime import datetime
from indicateurs.views import get_total_indicateur


@login_required(login_url='/connexion/')
def index_dashboard(request):
    # indicateurs au niveau national
    indicateurs = get_total_indicateur()

    # total national
    national = indicateurs[0]


    return render_to_response('dashboard/home.html', {'national': national},
                              context_instance=RequestContext(request))

