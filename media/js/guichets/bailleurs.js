$(document).ready(function() {
    $('label[for="id_etat"]').parent().css({'clear': 'left'});
    $('#id_creede').datepicker({
        changeMonth: true,
        changeYear: true
    });
    $('#id_creede').datepicker("option", $.datepicker.regional['fr']);
    $('#id_creea').datepicker({
        changeMonth: true,
        changeYear: true
    });
    $('#id_creea').datepicker("option", $.datepicker.regional['fr']);

    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/guichets/bailleurs/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "commune"},
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "40px" },
            { "sTitle": "Création", "mDataProp": "creation", "sWidth": "60px" },
            { "sTitle": "Bailleurs", "mDataProp": "bailleurs" },
            { "sTitle": "Etat", "mDataProp": "etat", "sWidth": "60px", "bSortable": false },
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fCode", "value": $('#id_code').val()},
                {"name": "fCreede", "value": $('#id_creede').val()},
                {"name": "fCreea", "value": $('#id_creea').val()},
                {"name": "fEtat", "value": $('#id_etat').val()},
                {"name": "fBailleur", "value": $('#id_bailleurs').val()}
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
    
    $('#btn_export').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/guichets/bailleurs/export/?' + data;
    });
} );