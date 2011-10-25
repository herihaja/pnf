$(document).ready(function(){
    $("#export-button").bind("click", function(){
        var temp = $("#action").val();
        $("#action").val("export");
        $("#form-filter").submit();
        $("#action").val(temp);
        return false;
    });

});
