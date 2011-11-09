# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
import xlwt
from datetime import datetime

def paginate(query, page_number, page):
    ''' pagine une liste a partir d'un queryset '''

    paginator = Paginator(query, page_number)

    try:
        pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pages = paginator.page(paginator.num_pages)

    return pages


def export_excel(header, input, subject):
    """ exporte au format excel les donnees dans la dictionnaire input, header est l'entete du tableau
    """

    filename = 'attachment; filename=%s-%s.xls' % (subject, datetime.strftime(datetime.now(), "%d%m%y"))
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = filename
    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet(subject.capitalize())
    gras = xlwt.easyxf("font: bold 1;")
    i = 0
    for elt in header:
        ws.write(0, i, u'%s' % elt, gras)
        i += 1

    i = 1 # parcours ligne
    for row in input:
        j = 0
        for elt in row:
            ws.write(i, j, elt)
            j += 1
        i += 1

    wb.save(response)
    return response

def process_datatables_posted_vars(post):
    posted = {}
    num_data = len(post) // 2
    for i in range (0,  num_data):
        key = "data[%s][name]" % (i,)
        value = "data[%s][value]" % (i,)
        posted[post[key]] = post[value]
    return posted