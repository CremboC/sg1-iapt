$(document).ready(function () {
    $.getJSON(__users_url__, function (data) {
        var $hiddenUserId = $('#filter_user_id');
        var users = $.map(data.users, function (u) {
            return u.username;
        });

        $("#filter_user").typeahead({
            source: users,
            autoSelect: true
        });
    });
});
