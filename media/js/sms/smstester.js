$(document).ready(function() {
    var limitNum = 160
    $('.edit-form input:submit').button();
    $('#accordion').accordion({ collapsible: false });

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
});