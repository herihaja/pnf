$(document).ready(function() {
    $('label[for="id_date_de"]').parent().css({'clear': 'left'});
    $('#id_date_de').datepicker({
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true,
        dateFormat: "mm/yy",
        onClose: function(dateText, inst) {
            var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
            var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
            $(this).datepicker('setDate', new Date(year, month, 1));
        },
        beforeShow : function(input, inst) {
            if ((datestr = $(this).val()).length > 0) {
                year = datestr.substring(datestr.length-4, datestr.length);
                month = parseInt(datestr.substring(3, 5))-1;
                $(this).datepicker('option', 'defaultDate', new Date(year, month, 1));
                $(this).datepicker('setDate', new Date(year, month, 1));
            }
        }
    });
    $('#id_date_de').focus(function () {
        $(".ui-datepicker-calendar").hide();
    });
    $('#id_date_de').datepicker("option", $.datepicker.regional['fr']);
    $('#id_date_a').datepicker({
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true,
        dateFormat: "mm/yy",
        onClose: function(dateText, inst) {
            var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
            var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
            $(this).datepicker('setDate', new Date(year, month, 1));
        },
        beforeShow : function(input, inst) {
            if ((datestr = $(this).val()).length > 0) {
                year = datestr.substring(datestr.length-4, datestr.length);
                month = parseInt(datestr.substring(3, 5))-1;
                $(this).datepicker('option', 'defaultDate', new Date(year, month, 1));
                $(this).datepicker('setDate', new Date(year, month, 1));
            }
        }
    });
    $('#id_date_a').datepicker("option", $.datepicker.regional['fr']);
    $('#id_date_a').focus(function () {
        $(".ui-datepicker-calendar").hide();
    });

    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/indicateurs/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "commune" },
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "60px", "bSortable": false },
            { "sTitle": "Période", "mDataProp": "periode", "sWidth": "60px" },
            { "sTitle": "Dem", "mDataProp": "demandes", "sWidth": "50px" },
            { "sTitle": "Opp", "mDataProp": "oppositions", "sWidth": "50px" },
            { "sTitle": "Res", "mDataProp": "resolues", "sWidth": "50px" },
            { "sTitle": "Cer", "mDataProp": "certificats", "sWidth": "50px" },
            { "sTitle": "Fem", "mDataProp": "femmes", "sWidth": "50px" },
            { "sTitle": "Sur", "mDataProp": "surfaces", "sWidth": "60px" },
            { "sTitle": "Rect", "mDataProp": "recettes", "sWidth": "80px" },
            { "sTitle": "Gar", "mDataProp": "garanties", "sWidth": "50px" },
            { "sTitle": "Reco", "mDataProp": "reconnaissances", "sWidth": "50px" },
            { "sTitle": "Mut", "mDataProp": "mutations", "sWidth": "50px" },
            { "sTitle": "Actions", "mDataProp": "actions", "sWidth": "80px" }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fCode", "value": $('#id_code').val()},
                {"name": "fCreede", "value": $('#id_date_de').val()},
                {"name": "fCreea", "value": $('#id_date_a').val()}
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
        window.location.href = '/indicateurs/export/?' + data;
    });
} );