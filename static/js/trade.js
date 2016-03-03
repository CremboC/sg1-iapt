function transferOptions(select1, select2){
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


