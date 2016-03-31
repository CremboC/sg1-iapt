function redirectToTrade(URL){
    var username = $('#trade_modal_username').val();
    URL += "?receiver_username="+username;
    window.location.replace(URL);
}

$(document).ready(function () {
    $.getJSON(__users_url__, function (data) {
        var $hiddenUserId = $('#trade_modal_username');
        var users = $.map(data.users, function (u) {
            return u.username;
        });

        $hiddenUserId.typeahead({
            source: users,
            autoSelect: true
        });
    });
});




$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});


$(document).on('change', '#objects_image', function() {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#preview").css({'background-image': 'url('+ e.target.result+')'});
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

$(document).on('click', '#objects_image', function() {
    $("#preview").css({'background-image': 'url()'});
    });