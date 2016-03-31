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
});
