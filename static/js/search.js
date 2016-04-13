$(document).ready(function () {
    // fill the typeahead for the users filter
    $.getJSON(__users_url__, function (data) {
        var users = $.map(data.users, function (u) {
            return u.username;
        });

        $("#filter_user").typeahead({
            source: users,
            autoSelect: true
        });
    });
});
