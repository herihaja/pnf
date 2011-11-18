$(document).ready(function() {
    $('label[for="id_region"]').parent().css({'clear': 'left'});
    oTable = $('#example').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "oLanguage": {"sUrl": "/media/js/datatables.french.txt"},
        "bFilter": false,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Tout"]],
        "sAjaxSource": '/indicateurs/annees/ajax/',
        "aoColumns": [
            { "sTitle": "Commune", "mDataProp": "nom", "bSortable": false },
            { "sTitle": "J", "mDataProp": "jan", "sWidth": "40px", "bSortable": false },
            { "sTitle": "F", "mDataProp": "fev", "sWidth": "40px", "bSortable": false },
            { "sTitle": "M", "mDataProp": "mar", "sWidth": "40px", "bSortable": false },
            { "sTitle": "A", "mDataProp": "avr", "sWidth": "40px", "bSortable": false },
            { "sTitle": "M", "mDataProp": "mai", "sWidth": "40px", "bSortable": false },
            { "sTitle": "J", "mDataProp": "jun", "sWidth": "40px", "bSortable": false },
            { "sTitle": "J", "mDataProp": "jul", "sWidth": "40px", "bSortable": false },
            { "sTitle": "A", "mDataProp": "aou", "sWidth": "40px", "bSortable": false },
            { "sTitle": "S", "mDataProp": "sep", "sWidth": "40px", "bSortable": false },
            { "sTitle": "O", "mDataProp": "oct", "sWidth": "40px", "bSortable": false },
            { "sTitle": "N", "mDataProp": "nov", "sWidth": "40px", "bSortable": false },
            { "sTitle": "D", "mDataProp": "dec", "sWidth": "40px", "bSortable": false },
            { "sTitle": "Moy", "mDataProp": "moy", "sWidth": "60px", "bSortable": false },
        ],
        "sPaginationType": "full_numbers",
        "bJQueryUI": true,
        "fnServerData": function (sSource, aoData, fnCallback) {
            aoData.push(
                {"name": "fRegion", "value": $('#id_region').val()},
                {"name": "fCommune", "value": $('#id_commune').val()},
                {"name": "fDistrict", "value": $('#id_district').val()},
                {"name": "fIndicateur", "value": $('#id_indicateur').val()},
                {"name": "fAnnee", "value": $('#id_annee').val()}
            );
            $.ajax({
                "dataType": 'json',
                "type": "POST",
                "url": sSource,
                "data": {"csrfmiddlewaretoken": csrf, "data": aoData},
                "success": function(result) {
                    $('#tot-national').html(result.national);
                    $('#tot-region').html(result.regional);
                    $('#tot-district').html(result.district);
                    fnCallback(result);
                }
            });
        },
        "sDom": 'rt<"F"lip>'
    });

    $('#form-filter').submit(function() {
        oTable.fnDraw();
        return false;
    });

    $('#id_region').live('change', function() {
        $('#id_district').html('<option value="">---</option>');
        $('#id_commune').html('<option value="">---</option>');
        $.ajax({
            type: 'POST',
            url: '/cascade/region/',
            data: {"csrfmiddlewaretoken": csrf, "region": $(this).val()},
            success: function(data) {
                var items = new Array();
                items.push('<option value="">---</option>');
                for (i = 0; i < data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_district').html(items.join(''));
            }
        });
    });

    $('#id_district').live('change', function() {
        $('#id_commune').html('<option value="">---</option>');
        $.ajax({
            type: 'POST',
            url: '/cascade/district/',
            data: {"csrfmiddlewaretoken": csrf, "district": $(this).val()},
            success: function(data) {
                var items = new Array();
                items.push('<option value="">---</option>');
                for (i = 0; i < data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_commune').html(items.join(''));
            }
        });
    });

    $('#btn_export').live('click', function() {
        var data = $("#form-filter").serialize();
        window.location.href = '/ratios/export/?' + data;
    });
});