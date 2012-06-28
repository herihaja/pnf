var url_delete = '/communications/supprimer/';
$(document).ready(function() {
    $('#id_cree_de').datepicker({
        changeMonth: true,
        changeYear: true
    });
    $('#id_cree_de').datepicker("option", $.datepicker.regional['fr']);
    $('#id_cree_a').datepicker({
        changeMonth: true,
        changeYear: true
    });
    $('#id_cree_a').datepicker("option", $.datepicker.regional['fr']);
    
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
            { "sTitle": "<input type=\"checkbox\" id=\"checkall\"/>", "mDataProp": "checkbox", "bSortable": false }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fMessage", "value": $('#id_message').val()},
                {"name": "fCreede", "value": $('#id_cree_de').val()},
                {"name": "fCreea", "value": $('#id_cree_a').val()}
            );
            $.ajax( {
                "dataType": 'json',
                "type": "POST",
                "url": sSource,
                "data": {"csrfmiddlewaretoken": csrf, "data": aoData},
                "success": fnCallback
            } );
        },
        "sDom": 'rt<"F"lip>',
        "fnDrawCallback": function( oSettings ) {
            bind_checkbox();
        },
        "aaSorting": [[ 0, "desc" ]]
    });

    $('#form-filter').submit(function(){
        oTable.fnDraw();
        return false;
    });

    $('#btn_export_xls').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/communications/export/xls/?' + data;
    });
    $('#btn_export_pdf').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/communications/export/pdf/?' + data;
    });
} );