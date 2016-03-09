function transferOptionsToTrade(select1, itemPreviewDiv, enableRemove) {
    var itemIds = select1.val();
    console.log(enableRemove);
    addItemToTrade(itemIds, itemPreviewDiv, select1, enableRemove);
}

function createOption(id, name) {
    return $("<option value='" + id + "'>" + name + "</option>")
}

function addItemToTrade(ids, displayDiv, availableSelect, enableRemove) {
    console.log(enableRemove);
    var joined_ids;
    if (ids instanceof Array) {
        joined_ids = ids.join();
    } else {
        joined_ids = [ids].join();
    }
    console.log(enableRemove);
    $.getJSON('getobjectdata?ids=' + joined_ids, function (data) {
        for (var x = 0; x < data.length; x++) {
            var object = data[x];
            console.log(enableRemove);
            displayDiv.append(makeObjectDisplay(object, availableSelect, enableRemove));
            availableSelect.children("option[value='" + object.id + "']").remove();
        }
    });

}

function makeObjectDisplay(object, availableSelect, enableRemove) {

    var div = $("<div itemid=" + object.id + " class='item-preview' style='background-image: url(" + object.image + ");'> </div>");
    var hovertext = $("<div class='hovertext'><p>" + object.name + "</p><p>Value: " + object['currency_value'] + " </div>");
    console.log(enableRemove);
    if (enableRemove) {
        var removeBtn = $("<div class='rmvItemPreview'><span class='glyphicon glyphicon glyphicon-remove' style='color:red'></span></div>");
        removeBtn.click(function () {
            $(this).parent().remove();
            availableSelect.append(createOption(object.id, object.name));

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
        console.log(this);
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
