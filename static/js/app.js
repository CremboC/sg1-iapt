/**
 * Redirects to a new after the modal for "create trade" is filled.
 * @param URL
 */
function redirectToTrade(URL) {
    var username = $('#trade_modal_username').val();
    URL += "?receiver_username=" + username;
    window.location.replace(URL);
}

/**
 * Set a parameter like ?<param>=<val>
 * @param paramName
 * @param paramValue
 */
function setGetParameter(paramName, paramValue) {
    var url = window.location.href;
    var hash = location.hash;

    url = url.replace(hash, '');

    if (url.indexOf(paramName + "=") >= 0) {
        var prefix = url.substring(0, url.indexOf(paramName));
        var suffix = url.substring(url.indexOf(paramName));

        suffix = suffix.substring(suffix.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    } else {
        if (url.indexOf("?") < 0) {
            url += "?" + paramName + "=" + paramValue;
        } else {
            url += "&" + paramName + "=" + paramValue;
        }
    }

    window.location.href = url + hash;
}


$(function () {
    $('[data-toggle="tooltip"]').tooltip();

    // image preview
    $(document).on('change', '#objects_image', function () {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#preview").css({'background-image': 'url(' + e.target.result + ')'});
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    $(document).on('click', '#objects_image', function () {
        $("#preview").css({'background-image': 'url()'});
    });

    // typeahead for users field in "create trade" modal
    $.getJSON(__users_url_ignore_auth__, function (data) {
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
