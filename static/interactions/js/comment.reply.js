/* global gettext */

$(document).ready(function () {
    const $container = $('#comment-container');

    function getCsrfToken($form) {
        return $form.find('[name=csrfmiddlewaretoken]').val() || $('input[name=csrfmiddlewaretoken]').first().val();
    }

    // Submit comment / reply
    $container.on('submit', '.comment-form', function (e) {
        e.preventDefault();
        const $form = $(this);
        const url = $form.attr('action');
        const formData = new FormData(this);
        const csrftoken = getCsrfToken($form);

       if (!csrftoken) {
            alert(gettext("CSRF token missing. Reload the page and try again."));
            return;
        }

        $.ajax({
            url: url,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (data) {
                if (data.success) {
                    // Replace toàn bộ container comment bằng HTML mới
                    $container.html(data.html);

                    // Reset form
                    $form[0].reset();
                    if ($form.hasClass('reply-form')) $form.addClass('d-none');
                } else {
                    alert("Có lỗi: " + JSON.stringify(data.errors));
                }
            },
            error: function (xhr, status, error) {
                alert(gettext("Failed to submit comment."));

            }
        });
    });
    // Toggle reply form
    $container.on('click', '.reply-btn', function () {
        const commentId = $(this).data('id');
        const $form = $(`#reply-form-${commentId}`);
        $form.toggleClass('d-none');
        if (!$form.hasClass('d-none')) $form.find('textarea').focus();
    });

    // Delete comment
    $container.on('click', '.delete-btn', function () {
        const commentId = $(this).data('id');
        const url = $(this).data('url');
        const csrftoken = $('input[name=csrfmiddlewaretoken]').first().val();
        
        $.ajax({
            url: url,
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (data) {
                if (data.success) $(`#comment-${commentId}`).remove();
            },
            error: function () {
                alert(gettext("Failed to delete comment."));
            }
        });
   });
});
