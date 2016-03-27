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