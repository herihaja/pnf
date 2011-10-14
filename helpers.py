from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
import xlwt

def paginate(query, page_number, page):
    ''' pagine une liste a partir d'un queryset '''

    paginator = Paginator(query, page_number)

    try:
        pages = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pages = paginator.page(paginator.num_pages)

    return pages


def export_excel(header, input, filename):
    ''' exporte au format execel les donnees dans la dictionnaire input, header est l'entete du tableau '''

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment; filename=%s.xls" % filename
    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet('Centres')
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