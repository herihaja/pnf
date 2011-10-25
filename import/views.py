import xlrd

def importer_donnees(request):
    book = xlrd.open_workbook("media/data2010.xls")
    sheet = book.sheets()[0]

    r = sheet.row(0) #returns all the CELLS of row 0,
    c = sheet.col_values(0) #returns all the VALUES of row 0,

    data = [] #make a data store
    for i in xrange(sheet.nrows):
        data.append(sheet.row_values(i))

    return render_to_response('donnees/importer_donnees.html', {"data": data},
                              context_instance=RequestContext(request))