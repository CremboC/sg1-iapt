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
    updateTradeValue();
}

function hideNonTradables(divId, checkboxId){
    var hide = $('#'+checkboxId).is(':checked');
    if (hide) {
        $('#' + divId).children('.item-preview').show();
    } else {
        $('#' + divId).children('.disabled').hide();
    }
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

//TODO: write search for items
$(function () {
    var opts = $('#yourItems').find('.item-preview').map(function () {
        console.log($(this).attr('class'));
        return [[$(this).data('itemid'), $(this).data('original-title')()]];
    });
    console.log(opts);
    $('#searchItems').keyup(function () {
        var rxp = $('#searchItems').val();
        console.log(rxp);
        var optlist = $('#yourItemDisplay').children('item-preview').hide();
        opts.each(function () {
            if (rxp.search(this[1])!=-1) {
                $('div[data-itemid='+this[0]+"]'").show();
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
    var opts = $('#theirAvailableObjects').find('option').map(function () {
        return [[this.value, $(this).text()]];
    });

    $('#searchTheirItems').keyup(function () {
        var rxp = new RegExp($('#searchTheirItems').val(), 'i');
        var optlist = $('#theirAvailableObjects').empty();
        opts.each(function () {
            if (rxp.test(this[1])) {
                optlist.append($('<option/>').attr('value', this[0]).text(this[1]));
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