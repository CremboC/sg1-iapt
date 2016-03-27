function create_collection(){
    var data = $("#new_collection").find(":input").serialize();
    $.ajax({
        url: new_col_url,
        type: "POST",
        data: data,
        success: function (data, textStatus, errorThrown){
            if (data == "-1"){
                // Flash error message in dialog
                var formgroup = $("#modal_collection_name");
                formgroup.addClass("has-error")
                formgroup.find("span").show();
            } else {
                // Append to list
                var col_name = $("#collections_name").val();
                var option = $("<option value="+data+">"+col_name+"</option>");
                var multiselect = $("#objects_collection");
                multiselect.append(option);
                multiselect.multiselect('rebuild');
                $("#new_collection").modal('hide');
            }
        },
        error: function (jXHR, textStatus, errorThrown){
            console.log("Error occured");
        }
    });
}