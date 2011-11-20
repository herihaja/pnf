$(document).ready(function() {
    $('.filter-form input:submit').button();
    $('.filter-form input:button').button();
    $('#accordion').accordion({ collapsible: true });
    $('#del-confirm').dialog({
        autoOpen: false,
        resizable: false,
        height:150,
        modal: true
    });

    $('.del-link').live('click', function(e) {
        e.preventDefault();
        var targetUrl = $(this).attr("href");
        $('#del-confirm').dialog({
            buttons : {
                "Supprimer": function() {
                    $.ajax({
                        "dataType": 'json',
                        "type": "POST",
                        "url": targetUrl,
                        "data": {"csrfmiddlewaretoken": csrf},
                        "success": function() {
                            oTable.fnDraw();
                        }
                    });
                    $(this).dialog("close");
                },
                "Annuler": function() {
                    $(this).dialog("close");
                }
            }
        });
        $('#del-confirm').dialog('open');
    });
});
