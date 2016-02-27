function transferOptions(select1, select2){
    var selectedItems = select1.children("option:selected");
    select1.children("option:selected").remove();
    select2.append(selectedItems);
    console.clear();
    console.log(select1);
    console.log(select2);

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

function submitproposal(senderId, receivedId, sentItemsSelect, receivedItemsSelect){
    var sentItems = sentItemsSelect.children("option").map(function(){return this.value}).get();
    var receivedItems = receivedItemsSelect.children("option").map(function(){return this.value}).get();
    var prevTrade = $.urlParam('tradeid');

    var data = {"prevTrade": prevTrade, "senderId": senderId, "receivedId": receivedId, "sentItems": sentItems, "receivedItems": receivedItems};
    $.ajax({
        type: "POST",
        url: "trade/newTrade",
        data: data,
        success: function(data, textStatus, xhr){
            window.location.href = "trade/home";
        },
        error: function(x, y, z) {
            console.log("fail");
        }
    });
}