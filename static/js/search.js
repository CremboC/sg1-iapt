function watcher($toWatch, $toUpdate) {
    $toWatch.change(function (e) {
        $toUpdate.html(e.target.value);
    });
}

$.getJSON(__users_url__, function (data) {
    var $hiddenUserId = $('#filter_user_id');
    var users = $.map(data.users, function (u) {
        return u.username;
    });

    $("#filter_user").typeahead({
        source: users,
        afterSelect: function (selectedUser) {
            var u = $.grep(data.users, function (user, index) {
                return (user.username == selectedUser);
            });
            $hiddenUserId.val(u[0].id);
        },
        autoSelect: true
    });
});

watcher($('#min_value'), $('#current_min_value'));
watcher($('#max_value'), $('#current_max_value'));