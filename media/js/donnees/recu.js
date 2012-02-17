var url_delete = '/recu/supprimer/0';
$(document).ready(function() {
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/recu/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "commune", "bSortable": false },
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Période", "mDataProp": "periode", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Dem", "mDataProp": "demandes", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Opp", "mDataProp": "oppositions", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Res", "mDataProp": "resolues", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Cert", "mDataProp": "certificats", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Fem", "mDataProp": "femmes", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Surf", "mDataProp": "surfaces", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Rect", "mDataProp": "recettes", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Gar", "mDataProp": "garanties", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Reco", "mDataProp": "reconnaissances", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Mut", "mDataProp": "mutations", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Dbl", "mDataProp": "doublon", "sWidth": "30px", "bSortable": false },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "80px", "bSortable": false },
            { "sTitle": "<input type=\"checkbox\" id=\"checkall\"/>", "mDataProp": "checkbox", "sWidth": "30px", "bSortable": false }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fCode", "value": $('#id_code').val()},
                {"name": "fDoublon", "value": $('#id_doublon').val()}
            );
            $.ajax({
                "dataType": 'json',
                "type": "POST",
                "url": sSource,
                "data": {"csrfmiddlewaretoken": csrf, "data": aoData},
                "success": fnCallback
            });
        },
        "sDom": 'rt<"F"lip>',
        "fnDrawCallback": function( oSettings ) {
            bind_checkbox();
        },
        "aaSorting": [[ 2, "desc" ]]
    });

    $('#form-filter').submit(function(){
        oTable.fnDraw();
        return false;
    });

    $('#id_region').live('change', function(){
        $('#id_district').html('<option value="">---</option>');
        $('#id_commune').html('<option value="">---</option>');
        $.ajax({
            type: 'POST',
            url: '/cascade/region/',
            data: {"csrfmiddlewaretoken": csrf, "region": $(this).val()},
            success: function(data){
                var items = new Array();
                items.push('<option value="">---</option>');
                for(i=0; i<data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_district').html(items.join(''));
            }
        });
    });

    $('#id_district').live('change', function(){
        $('#id_commune').html('<option value="">---</option>');
        $.ajax({
            type: 'POST',
            url: '/cascade/district/',
            data: {"csrfmiddlewaretoken": csrf, "district": $(this).val()},
            success: function(data){
                var items = new Array();
                items.push('<option value="">---</option>');
                for(i=0; i<data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_commune').html(items.join(''));
            }
        });
    });

    $('#btn_export_xls').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/recu/export/xls/?' + data;
    });
    $('#btn_export_pdf').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/recu/export/pdf/?' + data;
    });


} );
