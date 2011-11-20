$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/bailleurs/ajax/',
        "aoColumns": [
            { "sTitle": "Nom", "mDataProp": "nom" },
            { "sTitle": "Projet", "mDataProp": "projet" },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "80px" }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fNom", "value": $('#id_nom').val()},
                {"name": "fProjet", "value": $('#id_projet').val()}
            );
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

    $('#btn_export').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/bailleurs/export/?' + data;
    });
} );