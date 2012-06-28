$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/utilisateurs/ajax/',
        "aoColumns": [
            { "sTitle": "Identifiant", "mDataProp": "username" },
            { "sTitle": "Nom et prénoms", "mDataProp": "name", "bSortable": false },
            { "sTitle": "Actif", "mDataProp": "actif", "sWidth": "40px", "bSortable": false },
            { "sTitle": "Admin", "mDataProp": "staff", "sWidth": "40px", "bSortable": false },
            { "sTitle": "Créé le", "mDataProp": "created", "sWidth": "130px", "bSortable": false },
            { "sTitle": "Conneté le", "mDataProp": "last_login", "sWidth": "130px", "bSortable": false },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "140px", "bSortable": false }
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

    $('#btn_export_xls').live('click', function() {
        window.location.href = '/utilisateurs/export/xls';
    });
    $('#btn_export_pdf').live('click', function() {
        window.location.href = '/utilisateurs/export/pdf';
    });
    $('#btn_submit').css('display', 'none');
} );