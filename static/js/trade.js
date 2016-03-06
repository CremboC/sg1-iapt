function transferOptionsToTrade(select1, select2){
    var itemIds = select1.val();
    console.log(select1.val());
    console.log(itemIds);
    for (var x=0; x<itemIds.length; x++){
        var id = itemIds[x];
        console.log('/getobjectdata?id='+id);
        $.getJSON('getobjectdata?id='+id, function(data){
            console.log("GOt image");
            console.log(data);
            makeObjectDisplay(data[0]);
        });

    }

    var selectedItems = select1.children("option:selected");
    select1.children("option:selected").remove();
    select2.append(selectedItems);
}

function makeObjectDisplay(object){
    var div = $("<div style='background-image: url("+object.image+")';>");
    console.log('createdImage');
    $("#hisItemDisplay").append(div);
}


function transferOptionsToAvailable(select1, select2){
    var selectedItems = select1.children("option:selected");
    select1.children("option:selected").remove();
    select2.append(selectedItems);
}

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
};

function selectAll(){
    $("option").attr('selected', 'selected');
    console.log("Hello");
}


