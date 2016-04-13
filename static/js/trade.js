function moveObject(object) {
    var parentName = $(object).parent().attr('id');
    switch (parentName) {
        case "yourItems":
            $("#yourOffering").append(object);
            $(object).addClass("item-preview-in-trade");
            filterTradeItems(true);
            break;
        case "theirItems":
            $("#theirOffering").append(object);
            $(object).addClass("item-preview-in-trade");
            filterTradeItems(false);
            break;
        case "yourOffering":
            $("#yourItems").append(object);
            $(object).removeClass("item-preview-in-trade");
            filterTradeItems(true);
            break;
        case "theirOffering":
            $("#theirItems").append(object);
            $(object).removeClass("item-preview-in-trade");
            filterTradeItems(false);
            break;
    }
    updateTradeValue();
}

$(document).ready(updateTradeValue());


function updateTradeValue() {
    var hisVal = 0;
    var yourVal = 0;
    $(">div.item-preview", $("#yourOffering")).each(function () {
        yourVal += parseFloat($(this).attr('data-currency_value'));
    });
    $(">div.item-preview", $("#theirOffering")).each(function () {
        hisVal += parseFloat($(this).attr('data-currency_value'));
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

function deleteHiddenFormFields() {
    $("input[name=youritems]").remove();
    $("input[name=theiritems]").remove();
}


function filterTradeItems(yours) {
    console.log("FIlter");
    var divId, checkboxId, searchBoxId, selectId;
    if (yours) {
        divId = '#yourItems';
        checkboxId = '#your-item-checkbox';
        searchBoxId = '#searchOwnItems';
        selectId = '#selectOwnCol';
    } else {
        divId = '#theirItems';
        checkboxId = '#their-item-checkbox';
        searchBoxId = '#searchTheirItems';
        selectId = '#selectTheirCol';
    }
    $(divId).children('.item-preview').show();
    hideNonTradables(divId, checkboxId);
    filterByCollections(divId, selectId);
    filterByTerm(divId, searchBoxId);
}

function hideNonTradables(divId, checkboxId) {
    var hide = $(checkboxId).is(':checked');
    if (hide) {
        $(divId).children('.item-preview:visible').show();
    } else {
        $(divId).children('.disabled:visible').hide();
    }
}

function filterByCollections(divId, selectId) {
    var collection = $(selectId).val();
    console.log(collection);
    if (collection != "all") {
        $(divId).children('.item-preview:visible').each(function () {
            var collections = $(this).attr('data-collections');
            if (collections.indexOf(collection) == -1) {
                $(this).hide();
            }
        });
    }
}

function filterByTerm(divId, searchId) {
    var opts = $(divId).find('.item-preview:visible').map(function () {
        return [[$(this).attr('data-itemid'), $(this).attr('data-original-title')]];
    });
    var rxp = $(searchId).val();
    if (rxp != null) {
        rxp = rxp.toLowerCase();
    }
    opts.each(function () {
        var text = this[1].toLowerCase();
        var div = $('div[data-itemid=' + this[0] + "]");
        if (div.is(":visible")) {
            if (text.indexOf(rxp) == -1) {
                div.hide();
            }
        }
    });
}

$('#searchOwnItems').keyup(function () {
    filterTradeItems(true);
});

$('#searchTheirItems').keyup(function () {
    filterTradeItems(false);
});

$(function () {
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

function submitForm() {
    generateFormFields();
    var form = $("#tradeform");
    $.ajax({
        url: form.attr('action'),
        type: "POST",
        data: form.serialize(),
        success: function (data, textStatus, errorThrown) {
        },
        error: function (jXHR) {
            $(".alert").remove();
            var error = $("<div class='alert alert-danger' role='alert'>" + jXHR.responseText + "</div>");
            var closeError = $("<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>");
            error.append(closeError);
            $("#errorcontainer").prepend(error);
            deleteHiddenFormFields();
        }
    });
}
