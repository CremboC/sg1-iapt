/**
 * Helper function to create an input which allows the removal of objects
 * @param id
 * @returns {*|jQuery|HTMLElement}
 */
function createInput(id) {
    return $('<input type="hidden" name="objects_to_remove" value="' + id + '" id="object-removal-' + id + '">');
}

$(document).ready(function () {

    // cache all used DOM objects
    var $form = $('#collection_form'),
        $toggleRemoveButton = $('#toggle-remove'),
        $submit = $('#submit_button'),
        $undo = $('.undo'),
        $undoText = $("#undo-name-display"),
        $objectRemove = $('.object-remove');

    // stores objects to be removed
    var objects = [];

    // init by hiding elements that need to be hidden
    $undo.hide();
    $submit.hide();
    $objectRemove.hide();

    // toggle whether removing items is enabled or not
    $toggleRemoveButton.on('click', function (e) {
        e.preventDefault();
        $objectRemove.toggle();
    });

    $('.remove').on('click', function (e) {
        e.preventDefault();

        var objectId = $(this).data('id');
        $form.append(createInput(objectId));

        objects.push(objectId);

        $undo.show();
        $undoText.text(
            $( "#object-" + objectId + " .object-name" ).text().trim()
        );
        $('#object-' + objectId).hide();
        $('body').css({
            'margin-bottom': '80px'
        });

        $submit.show();
    });

    $undo.find('a').on('click', function (e) {
        e.preventDefault();
        console.log('yes');

        var objectId = objects[objects.length - 1];

        $('#object-removal-' + objectId).remove();
        $('#object-' + objectId).show();

        objects.pop();

        if (objects.length == 0) {
            $undo.hide();
            $submit.hide();
        }
    });

    $('#new_objects').multiselect({
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        filterBehavior: 'text',
        buttonWidth: '350px'
    });
});
