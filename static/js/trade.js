function transferOptionsToTrade(select1, itemPreviewDiv, enableRemove) {
    var itemIds = select1.val();
    addItemToTrade(itemIds, itemPreviewDiv, select1, enableRemove);
}

function createOption(id, name, currency_value) {
    return $("<option value='" + id + "' data-currency_value="+currency_value+">" + name + "</option>")
}

function addItemToTrade(ids, displayDiv, availableSelect, enableRemove) {
    var joined_ids;
    if (ids instanceof Array) {
        joined_ids = ids.join();
    } else {
        joined_ids = [ids].join();
    }
    $.getJSON('getobjectdata?ids=' + joined_ids, function (data) {
        for (var x = 0; x < data.length; x++) {
            var object = data[x];
            displayDiv.append(makeObjectDisplay(object, availableSelect, enableRemove));
            availableSelect.children("option[value='" + object.id + "']").remove();
        }
        updateTradeValue($("#yourItemDisplay"), $("#hisItemDisplay"))
    });
}

function updateTradeValue(yourItems, hisItems){

    var totalVal = 0;
    $(">div", yourItems).each(function(){
        totalVal-=parseFloat($(this).attr('data-currency_value'));
    });
    $(">div", hisItems).each(function(){
        totalVal+=parseFloat($(this).attr('data-currency_value'));
    });
    if (isNaN(totalVal)){
        totalVal = 0;
    } else {
        totalVal.toFixed(2);
    }
    $("#tradevalue").text(totalVal);
}


function makeObjectDisplay(object, availableSelect, enableRemove) {

    var div = $("<div  data-currency_value="+object.currency_value+" itemid=" + object.id + " class='item-preview' style='background-image: url(" + object.image + ");'> </div>");
    var hovertext = $("<div class='hovertext'></div>");
    var name = $("<div style='clear:both'>"+object.name+"</div>");
    var value = $("<div style='clear:both'><span class='glyphicon glyphicon-gbp object-icon'></span>"+object['currency_value']+"</div>");
    hovertext.append(name);
    hovertext.append(value);

    if (enableRemove) {
        var removeBtn = $("<div class='rmvItemPreview'><span class='glyphicon glyphicon glyphicon-remove' style='color:red'></span></div>");
        removeBtn.click(function () {
            $(this).parent().remove();
            availableSelect.append(createOption(object.id, object.name, object.currency_value));
            updateTradeValue($("#yourItemDisplay"), $("#hisItemDisplay"))
        });
        div.append(removeBtn).append(hovertext);
    } else {
        div.append(hovertext);
    }
    $("#hisItemDisplay").append(div);
    return div
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
    $("#yourItemDisplay").children('div').each(function () {
        yourItemIds.push($(this).attr('itemid'));
    });

    var hisItemIds = [];
    $("#hisItemDisplay").children('div').each(function () {
        hisItemIds.push($(this).attr('itemid'));
    });
    var yourItems = $('<input style="display:none" name="youritems" value="' + yourItemIds + '">');
    var hisItems = $("<input style='display:none' name='theiritems' value=" + hisItemIds + ">");
    $("#tradeform").append(yourItems).append(hisItems);

}

function deleteHiddenFormFields(){
    $("input[name=youritems]").remove();
    $("input[name=theiritems]").remove();
}

$(function () {
    var opts = $('#ownAvailableObjects').find('option').map(function () {
        return [[this.value, $(this).text()]];
    });


    $('#searchOwnItems').keyup(function () {
        var rxp = new RegExp($('#searchOwnItems').val(), 'i');
        var optlist = $('#ownAvailableObjects').empty();
        opts.each(function () {
            if (rxp.test(this[1])) {
                optlist.append($('<option/>').attr('value', this[0]).text(this[1]));
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