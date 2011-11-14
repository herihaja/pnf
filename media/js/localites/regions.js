$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/localites/regions/ajax/',
        "aoColumns": [
            { "sTitle": "Region", "mDataProp": "nom", "bSortable": false },
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "80px", "bSortable": false }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "sDom": 'rt<"F"li>'
    });

    $('#btn_export').live('click', function() {
        window.location.href = '/localites/regions/export/';
    });
} );