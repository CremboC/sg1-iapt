function transferOptionsToTrade(select1, itemPreviewDiv){
    var itemIds = select1.val();
    for (var x=0; x<itemIds.length; x++){
        var id = itemIds[x];
        addItemToTrade(id, itemPreviewDiv, select1, select1.find("option[value='"+id+"']"))
    }
    select1.children("option:selected").remove();
}

function createOption(id, name){
    return $("<option value='"+id+"'>"+name+"</option>")
}

function addItemToTrade(id, displayDiv, availableSelect, option){
   $.getJSON('getobjectdata?id='+id, function(data){
       displayDiv.append(makeObjectDisplay(data[0], availableSelect, option));
   });
}

function makeObjectDisplay(object, availableSelect, option){

    var div = $("<div itemid="+object.id+" class='item-preview' style='background-image: url("+object.image+")';> </div>");
    var hovertext = $("<div class='hovertext'><p>"+object.name+"</p><p>Value: " +object['currency_value']+ " </div>");
    var removeBtn = $("<div class='rmvItemPreview'><span class='glyphicon glyphicon glyphicon-remove' style='color:red'></span></div>");
    removeBtn.click(function(){
        $(this).parent().remove();
        availableSelect.append(option);

    });
    div.append(removeBtn).append(hovertext);
    $("#hisItemDisplay").append(div);
    return div
}

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }else{
       return results[1] || 0;
    }
};

function generateFormFields(){
    var yourItemIds = [];
    $("#yourItemDisplay").children('div').each(function(){
        console.log(this);
        yourItemIds.push($(this).attr('itemid'));
    });

    var hisItemIds = [];
    $("#hisItemDisplay").children('div').each(function(){
        hisItemIds.push($(this).attr('itemid'));
    });
    var yourItems = $("<input style='display:none' name='youritems' value="+yourItemIds+">");
    var hisItems = $("<input style='display:none' name='theiritems' value="+hisItemIds+">");
    $("#tradeform").append(yourItems).append(hisItems);
}

$(function() {
    var opts = $('#ownAvailableObjects option').map(function(){
        return [[this.value, $(this).text()]];
    });


    $('#searchOwnItems').keyup(function(){
        var rxp = new RegExp($('#searchOwnItems').val(), 'i');
        var optlist = $('#ownAvailableObjects').empty();
        opts.each(function(){
            if (rxp.test(this[1])) {
                optlist.append($('<option/>').attr('value', this[0]).text(this[1]));
            }
        });

    });

});

$(function() {
    var opts = $('#theirAvailableObjects option').map(function(){
        return [[this.value, $(this).text()]];
    });

    $('#searchTheirItems').keyup(function(){
        var rxp = new RegExp($('#searchTheirItems').val(), 'i');
        var optlist = $('#theirAvailableObjects').empty();
        opts.each(function(){
            if (rxp.test(this[1])) {
                optlist.append($('<option/>').attr('value', this[0]).text(this[1]));
            }
        });
    });
});








