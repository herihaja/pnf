
function bind_checkbox(){
    $("#checkall").attr("checked", false);
    $("#checkall").unbind().bind("click", function(){
        var checked = ($(this).attr("checked") == "checked");
        $(".check-element").attr("checked", checked);
    })

    $("#bulk-delete").unbind().bind("click", function(){
        var checked = new Array();
        $(".check-element:checked").each(function(){
            checked.push($(this).val());
        });

        $.post(url_delete, {'selected': checked},function(){
                oTable.fnDraw();
            }
        );
    })
}