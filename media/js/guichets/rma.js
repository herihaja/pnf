$(document).ready(function() {
    $('#id_periode').datepicker({
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true,
        regional: "fr",
        dateFormat: "mm/yy",
        onClose: function(dateText, inst) {
            var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
            var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
            $(this).datepicker('setDate', new Date(year, month, 1));
        },
        beforeShow : function(input, inst) {
            if ((datestr = $(this).val()).length > 0) {
                var year = datestr.substring(datestr.length-4, datestr.length);
                var month = parseInt(datestr.substring(0, 2), 10)-1;
                $(this).datepicker('option', 'defaultDate', new Date(year, month, 1));
                $(this).datepicker('setDate', new Date(year, month, 1));
            }
        }
    });
    $('#id_periode').focus(function () {
        $(".ui-datepicker-calendar").hide();
    });

    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/rma/envoi/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "commune" },
            { "sTitle": "Période", "mDataProp": "periode", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Reçu", "mDataProp": "reception", "sWidth": "140px", "bSortable": false },
            { "sTitle": "Région", "mDataProp": "region"},
            { "sTitle": "District", "mDataProp": "district"},
            { "sTitle": "Sms", "mDataProp": "statut", "sWidth": "60px", "bSortable": false },
            { "sTitle": "AGF", "mDataProp": "agf", "sWidth": "60px", "bSortable": false }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fAgf", "value": $('#id_agf').val()},
                {"name": "fPeriode", "value": $('#id_periode').val()},
                {"name": "fStatut", "value": $('#id_etat').val()}
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
    
    $('#btn_export_xls').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/rma/envoi/export/xls/?' + data;
    });
    $('#btn_export_pdf').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/rma/envoi/export/pdf/?' + data;
    });
} );