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