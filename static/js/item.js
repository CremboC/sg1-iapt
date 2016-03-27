$(document).ready(function () {
    var summaryCharLimit = 100;
    $('#objects_collection').multiselect({
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        filterBehavior: 'text',
        buttonWidth: '300px'
    });

    var $summaryLengthWrapper = $('#summary-length');
    $('#objects_summary').on('input', function (e) {
        if (this.value.length > summaryCharLimit) {
            this.value = this.value.substring(0, summaryCharLimit);
        } else {
            $summaryLengthWrapper.html(summaryCharLimit - this.value.length);
        }
    });
});
$('input:radio[name="status"]').change(function(){

    var multiselect =  $("#objects_collection");
    var div = $("#collections");
    if ($(this).val()==1){
        //multiselect.multiselect("deselectAll", false);
        //Disable collections select, remove any selected options
        div.slideUp();
        multiselect.multiselect('disable');

    } else {
        //Enable collection select, if none selected select
        multiselect.multiselect('enable');
        div.find("> option").each(function() {
            console.log($(this).innerHTML);
            if ($(this).innerHTML == "Unfiled") {
                $(this).prop("selected", true);
            }
        });
        multiselect.multiselect('rebuild');
        div.slideDown();
    }

});

function create_collection(){
    var data = $("#new_collection").find(":input").serialize();
    $.ajax({
        url: new_col_url,
        type: "POST",
        data: data,
        success: function (data, textStatus, errorThrown){
            var error,closeError;
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
                error = $("<div class='alert alert-success' role='alert'>Created new collection: " + col_name+".</div>");
                closeError = $("<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>");
                error.append(closeError);
                $("#errorcontainer").prepend(error);
                $("#new_collection").modal('hide');

            }
        },
        error: function (jXHR, textStatus, errorThrown){
            console.log("Error occured");
        }
    });
}