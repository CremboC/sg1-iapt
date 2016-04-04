function moveObject(object){
    var parentName = $(object).parent().attr('id');
    switch (parentName){
        case "yourItems":
            $("#yourOffering").append(object);
            break;
        case "theirItems":
            $("#theirOffering").append(object);
            break;
        case "yourOffering":
            $("#yourItems").append(object);
            break;
        case "theirOffering":
            $("#theirItems").append(object);
            break;
    }
    hideNonTradables('theirItems','their-item-checkbox', 'searchTheirItems');
    hideNonTradables('yourItems','your-item-checkbox', 'searchOwnItems');
    updateTradeValue();
}

$(document).ready(updateTradeValue());


function updateTradeValue(){
    var hisVal = 0;
    var yourVal = 0;
    $(">div.item-preview", $("#yourOffering")).each(function(){
        yourVal+=parseFloat($(this).attr('data-currency_value'));
    });
    $(">div.item-preview", $("#theirOffering")).each(function(){
        hisVal+=parseFloat($(this).attr('data-currency_value'));
    });
    var totalVal = hisVal - yourVal;
    totalVal = isNaN(totalVal) ? 0 : totalVal.toFixed(2);
    yourVal = isNaN(yourVal) ? 0 : yourVal.toFixed(2);
    hisVal = isNaN(hisVal) ? 0 : hisVal.toFixed(2);

    $("#tradevalue").text(totalVal);
    $("#yourVal").text(yourVal);
    $("#hisVal").text(hisVal);
}

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    } else {
        return results[1] || 0;
    }
};

function generateFormFields() {
    var yourItemIds = [];
    $(">div.item-preview", $("#yourOffering")).each(function () {
        yourItemIds.push($(this).attr('data-itemid'));
    });

    var hisItemIds = [];
    $(">div.item-preview", $("#theirOffering")).each(function () {
        hisItemIds.push($(this).attr('data-itemid'));
    });
    var yourItems = $('<input style="display:none" name="youritems" value="' + yourItemIds + '">');
    var hisItems = $("<input style='display:none' name='theiritems' value=" + hisItemIds + ">");
    $("#tradeform").append(yourItems).append(hisItems);

}

function deleteHiddenFormFields(){
    $("input[name=youritems]").remove();
    $("input[name=theiritems]").remove();
}

function hideNonTradables(divId, checkboxId, searchBox){
    var hide = $('#'+checkboxId).is(':checked');
    if (hide) {
        $('#' + divId).children('.item-preview').show();
    } else {
        $('#' + divId).children('.disabled').hide();
    }
    $('#'+searchBox).keyup();
}




$(function () {
    $('#searchOwnItems').keyup(function () {
        var opts = $('#yourItems').find('.item-preview').map(function () {
            return [[$(this).attr('data-itemid'), $(this).attr('data-original-title')]];
        });
        var rxp = $('#searchOwnItems').val().toLowerCase();
        opts.each(function () {
            var text = this[1].toLowerCase();
            var div = $('div[data-itemid='+this[0]+"]");
            if (text.indexOf(rxp)!=-1) {
                if (div.hasClass("disabled")){
                    if ($("#your-item-checkbox").is(':checked')){
                        div.show();
                    } else {
                        div.hide();
                    }
                } else {
                    div.show();
                }
            } else {
                div.hide();
            }
        });
    });

    $.getJSON(__users_url__, function (data) {
        var users = $.map(data.users, function (u) {
            return u.username;
        });

        $("#receiver_username").typeahead({
            source: users,
            afterSelect: function (selectedUser) {
            },
            autoSelect: true
        });
    });

});

$(function () {
    $('#searchTheirItems').keyup(function () {
        var opts = $('#theirItems').find('.item-preview').map(function () {
            return [[$(this).attr('data-itemid'), $(this).attr('data-original-title')]];
        });
        var rxp = $('#searchTheirItems').val().toLowerCase();
        opts.each(function () {
            var text = this[1].toLowerCase();
            var div = $('div[data-itemid='+this[0]+"]");
            if (text.indexOf(rxp)!=-1) {
                if (div.hasClass("disabled")){
                    if ($("#their-item-checkbox").is(':checked')){
                        div.show();
                    } else {
                        div.hide();
                    }
                } else {
                    div.show();
                }
            } else {
                div.hide();
            }
        });
    });
});

function submitForm(){
    generateFormFields();
    var form = $("#tradeform");
    $.ajax({
        url: form.attr('action'),
        type: "POST",
        data: form.serialize(),
        success: function (data, textStatus, errorThrown){
        },
        error: function (jXHR, textStatus, errorThrown){
            $(".alert").remove();
            var error = $("<div class='alert alert-danger' role='alert'>"+jXHR.responseText+"</div>");
            var closeError = $("<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>");
            error.append(closeError);
            $("#errorcontainer").prepend(error);
            deleteHiddenFormFields();
        }
    });
}