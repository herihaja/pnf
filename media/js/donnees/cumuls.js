$(document).ready(function() {
    $('label[for="id_demandes"]').parent().css({'clear': 'left'});
    $('label[for="id_recettes"]').parent().css({'clear': 'left'});
    $('label[for="id_periode_de"]').parent().css({'clear': 'left'});

    $('#id_periode_de').datepicker({
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
    $('#id_periode_de').focus(function () {
        $(".ui-datepicker-calendar").hide();
    });
    $('#id_periode_de').datepicker("option", $.datepicker.regional['fr']);
    $('#id_periode_a').datepicker({
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
    $('#id_periode_a').datepicker("option", $.datepicker.regional['fr']);
    $('#id_periode_a').focus(function () {
        $(".ui-datepicker-calendar").hide();
    });

    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/cumuls/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "commune" },
            { "sTitle": "Code", "mDataProp": "code", "sWidth": "60px" },
            { "sTitle": "Période", "mDataProp": "periode", "sWidth": "60px" },
            { "sTitle": "Dem", "mDataProp": "demandes", "sWidth": "40px" },
            { "sTitle": "Opp", "mDataProp": "oppositions", "sWidth": "40px" },
            { "sTitle": "Res", "mDataProp": "resolues", "sWidth": "40px" },
            { "sTitle": "Cer", "mDataProp": "certificats", "sWidth": "40px" },
            { "sTitle": "Fem", "mDataProp": "femmes", "sWidth": "40px" },
            { "sTitle": "Sur", "mDataProp": "surfaces", "sWidth": "60px" },
            { "sTitle": "Rect", "mDataProp": "recettes", "sWidth": "60px" },
            { "sTitle": "Gar", "mDataProp": "garanties", "sWidth": "40px" },
            { "sTitle": "Reco", "mDataProp": "reconnaissances", "sWidth": "40px" },
            { "sTitle": "Mut", "mDataProp": "mutations", "sWidth": "40px" }
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fCode", "value": $('#id_code').val()},
                {"name": "fDemandes", "value": $('#id_demandes').val()},
                {"name": "fOppositions", "value": $('#id_oppositions').val()},
                {"name": "fResolues", "value": $('#id_resolues').val()},
                {"name": "fCertificats", "value": $('#id_certificats').val()},
                {"name": "fFemmes", "value": $('#id_femmes').val()},
                {"name": "fRecettes", "value": $('#id_recettes').val()},
                {"name": "fMutations", "value": $('#id_mutations').val()},
                {"name": "fGaranties", "value": $('#id_garanties').val()},
                {"name": "fSurfaces", "value": $('#id_surfaces').val()},
                {"name": "fReconnaissances", "value": $('#id_reconnaissances').val()},
                {"name": "fPeriodeDe", "value": $('#id_periode_de').val()},
                {"name": "fPeriodeA", "value": $('#id_periode_a').val()}
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
        window.location.href = '/cumuls/export/xls/?' + data;
    });
    $('#btn_export_pdf').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/cumuls/export/pdf/?' + data;
    });
} );