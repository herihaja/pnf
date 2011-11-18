$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/communications/ajax/',
        "aoColumns": [
            { "sTitle": "Date / Heure", "mDataProp": "date_reception", "sWidth": "100px" },
            { "sTitle": "Commune", "mDataProp": "commune" },
            { "sTitle": "Code", "mDataProp": "code" },
            { "sTitle": "Message", "mDataProp": "message", "bSortable": false, "sWidth": "400px" },
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            $.ajax( {
                "dataType": 'json',
                "type": "POST",
                "url": sSource,
                "data": {"csrfmiddlewaretoken": csrf, "data": aoData},
                "success": fnCallback
            } );
        },
        "sDom": 'rt<"F"lip>'
    });

    $('#form-filter').submit(function(){
        oTable.fnDraw();
        return false;
    });
} );