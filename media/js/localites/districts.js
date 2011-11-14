$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/localites/districts/ajax/',
        "aoColumns": [
            { "sTitle": "District", "mDataProp": "nom" },
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "60px" },
            { "sTitle": "Région", "mDataProp": "region" },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "80px" }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fCode", "value": $('#id_code').val()}
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
        window.location.href = '/localites/districts/export/?' + data;
    });
});