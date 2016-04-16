/**
 * Method to move a trade object from the your items to offering sections
 * @param object
 */
function moveObject(object) {
    // Switch based on object's current location to select destination
    // Your items <--> Your offerings
    // Their items <--> Their offerings
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
// Method to update numbers displayed at bottom of trade page on page load
$(document).ready(updateTradeValue());

// Method to update numbers displayed at bottom of trade page
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
    // Prevent NaN from being displayed in case of error
    totalVal = isNaN(totalVal) ? 0 : totalVal.toFixed(2);
    yourVal = isNaN(yourVal) ? 0 : yourVal.toFixed(2);
    hisVal = isNaN(hisVal) ? 0 : hisVal.toFixed(2);

    $("#tradevalue").text(totalVal);
    $("#yourVal").text(yourVal);
    $("#hisVal").text(hisVal);
}

// Method to retrieve parameters from URL
$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    } else {
        return results[1] || 0;
    }
};

/**
 * Method to convert items in offerings into a list of item id's for submission to the server
 */
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

/**
 * Method to reset the trade's processed form fields
 */
function deleteHiddenFormFields() {
    $("input[name=youritems]").remove();
    $("input[name=theiritems]").remove();
}


/**
 * Method to apply the filters to trade items
 * @param yours: boolean True if yourItems, false if theirItems
 */
function filterTradeItems(yours) {
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

// First hide non-tradable items if enabled, otherwise show all
function hideNonTradables(divId, checkboxId) {
    var hide = $(checkboxId).is(':checked');
    if (hide) {
        $(divId).children('.item-preview:visible').show();
    } else {
        $(divId).children('.disabled:visible').hide();
    }
}

// Then hide all still visible items which do not belong to
// chosen collection, or do nothing if "all" collections is selected
function filterByCollections(divId, selectId) {
    var collection = $(selectId).val();
    if (collection != "all") {
        $(divId).children('.item-preview:visible').each(function () {
            var collections = $(this).attr('data-collections');
            if (collections.indexOf(collection) == -1) {
                $(this).hide();
            }
        });
    }
}

// Then filter by item name by searching item's name using keyword from input
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

// Dynamically apply filters on keyword edit
$('#searchOwnItems').keyup(function () {
    filterTradeItems(true);
});

$('#searchTheirItems').keyup(function () {
    filterTradeItems(false);
});


$(function () {
    // Get user data
    $.getJSON(__users_url__, function (data) {
        var users = $.map(data.users, function (u) {
            return u.username;
        });
    });

});

/**
 * Method to submit the form to the server and display any errors returned from server
 */
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
            // Error message passed through jXHR
            $(".alert").remove();
            var error = $("<div class='alert alert-danger' role='alert'>" + jXHR.responseText + "</div>");
            var closeError = $("<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>");
            error.append(closeError);
            $("#errorcontainer").prepend(error);
            deleteHiddenFormFields();
        }
    });
}
