$(document).ready(function() {
    $('.edit-form input:submit').button();
    /* COMPTEUR DE CARACTERES */
    var limitNum = 160
    function limitText(limitField, limitNum) {
        if (limitField.val().length > limitNum) {
            limitField.val(limitField.val().substring(0, limitNum));
        }
        nchar = limitNum - limitField.val().length;
        $('#nchar').html(nchar + ' caractères restants.');
    }

    $('#id_message').keyup(function() {
        limitText($(this), limitNum)
    });

    $('#id_message').keydown(function() {
        limitText($(this), 160)
    });

    nchar = limitNum - $('#id_message').val().length;
    $('#nchar').html(nchar + ' caractères restants.');

    /* VALIDATION FORMULAIRE */
    $('#tester-form').submit(function() {
        if($('#id_expediteur').val() == '') {
            alert('Numéro de téléphone obligatoire!');
            return false;
        }

        if($('#id_message').val() == '') {
            alert('Message obligatoire!');
            return false;
        }

        $(this).submit();
    });


    /* SELECTION DES DESTINATAIRES */
    function update_destinataires(loc, val) {
        $.ajax({
            type: 'POST',
            url: '/broadcast/ajax/',
            data: {"csrfmiddlewaretoken": csrf, 'localite': loc, 'value': val},
            success: function(data){
                $('#id_destinataire').val(data['numeros']);
                nb = data['numeros'].length;
                if(nb == 0) {
                    compte = 'Aucun numéro sélectionné';
                } else if(nb == 1) {
                    compte = data['numeros'];
                } else {
                    compte =  nb + ' numéros selectionnés'
                }
                $('#id_liste').val(compte);
            }
        });
    }

    $('#id_region').live('change', function(){
        $('#id_district').html('<option value="">---</option>');
        $('#id_commune').html('<option value="">---</option>');
        var id = $(this).val();
        $.ajax({
            type: 'POST',
            url: '/cascade/region/',
            data: {"csrfmiddlewaretoken": csrf, "region": id},
            success: function(data){
                var items = new Array();
                items.push('<option value="">---</option>');
                for(i=0; i<data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_district').html(items.join(''));
                update_destinataires('region', id);
            }
        });
    });

    $('#id_district').live('change', function(){
        $('#id_commune').html('<option value="">---</option>');
        var id = $(this).val();
        $.ajax({
            type: 'POST',
            url: '/cascade/district/',
            data: {"csrfmiddlewaretoken": csrf, "district": id},
            success: function(data){
                var items = new Array();
                items.push('<option value="">---</option>');
                for(i=0; i<data.length; i++) {
                    items.push('<option value="' + data[i].id + '">' + data[i].nom + '</option>');
                }
                $('#id_commune').html(items.join(''));
                update_destinataires('district', id);
            }
        });
    });

    $('#id_commune').live('change', function(){
        update_destinataires('commune', $(this).val());
    });
} );