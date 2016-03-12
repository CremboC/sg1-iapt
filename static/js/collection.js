function createInput(id) {
    return $('<input type="hidden" name="objects_to_remove" value="' + id + '" id="object-removal-' + id + '">');
}

$(document).ready(function () {

    var $form = $('.content').find('form');
    var $undo = $('.undo');
    var objects = [];

    $undo.hide();

    $('.remove').on('click', function (e) {
        e.preventDefault();

        var objectId = $(this).data('id');
        $form.append(createInput(objectId));

        $('#object-' + objectId).hide();

        objects.push(objectId);

        $undo.show();
        $('body').css({
            'margin-bottom': '60px'
        })
    });

    $undo.find('a').on('click', function (e) {
        e.preventDefault();
        console.log('yes');

        var objectId = objects[objects.length - 1];

        $('#object-removal-' + objectId).remove();
        $('#object-' + objectId).show();

        objects.pop();

        if (objects.length == 0) $undo.hide();
    });

    $('#new_objects').multiselect({
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        filterBehavior: 'text',
        buttonWidth: '350px'
    });


});