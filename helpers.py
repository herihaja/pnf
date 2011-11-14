# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
import xlwt
from datetime import datetime

def export_excel(header, dataset, topic):
    filename = 'attachment; filename=%s-%s.xls' % (topic, datetime.strftime(datetime.now(), "%d%m%y"))
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = filename
    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet(topic.capitalize())
    gras = xlwt.easyxf("font: bold 1;")
    i = 0
    for elt in header:
        ws.write(0, i, u'%s' % elt, gras)
        i += 1

    i = 1 # parcours ligne
    for row in dataset:
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

def query_datatables(model, columns, posted_data, **kwargs):
    # ordering
    sorts = []
    if 'iSortingCols' in posted_data:
        for i in range(0, int(posted_data['iSortingCols'])):
            sort_col = "iSortCol_%s" % (i,)
            sort_dir = posted_data["sSortDir_%s" % (i,)]
            if columns[int(posted_data[sort_col])] == 'code':  # code
                if sort_dir == "asc":
                    sort_qry = "commune__code"
                else:
                    sort_qry = "-commune__code"
            else:
                if sort_dir == "asc":
                    sort_qry = columns[int(posted_data[sort_col])]
                else:
                    sort_qry = "-%s" % (columns[int(posted_data[sort_col])],)
            sorts.append(sort_qry)

    # limitting
    lim_start = None
    lim_num = 25
    if 'iDisplayStart' in posted_data and posted_data['iDisplayLength'] != '-1':
        lim_start = int(posted_data['iDisplayStart'])
        lim_num = int(posted_data['iDisplayLength']) + lim_start

    # querying
    total_records = model.objects.count()
    if len(sorts) > 0:
        if lim_start is not None:
            result = model.objects.filter(**kwargs).order_by(*sorts)[lim_start:lim_num]
        else:
            result = model.objects.filter(**kwargs).order_by(*sorts)
    else:
        if lim_start is not None:
            result = model.objects.filter(**kwargs)[lim_start:lim_num]
        else:
            result = model.objects.filter(**kwargs)
    display_records = model.objects.filter(**kwargs).count()

    return result, total_records, display_records

def create_compare_condition(field, value):
    value = value.strip()
    if value[0:1] == '>':
        if value[1:2] == '=':
            key = '%s__gte' % (field,)
            value = value[2:].lstrip()
        else:
            key = '%s__gt' % (field,)
            value = value[1:].lstrip()
    elif value[0:1] == '<':
        if value[1:2] == '=':
            key = '%s__lte' % (field,)
            value = value[2:].lstrip()
        else:
            key = '%s__lt' % (field,)
            value = value[1:].lstrip()
    elif value[0:1] == '=':
        if value[1:2] == '<':
            key = '%s__lte' % (field,)
            value = value[2:].lstrip()
        elif value[1:2] == '>':
            key = '%s__gte' % (field,)
            value = value[2:].lstrip()
        else:
            key = '%s__lt' % (field,)
            value = value[1:].lstrip()
    else:
        key = field
        value = value
    return key, float(value)