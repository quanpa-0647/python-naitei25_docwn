/* global gettext */

$(document).ready(function () {
  const $container = $('#comment-container');

  // Hàm lấy CSRF token
  function getCsrfToken($form) {
    return $form.find('[name=csrfmiddlewaretoken]').val() || $('input[name=csrfmiddlewaretoken]').first().val();
  }

  // Submit comment / reply form bằng AJAX
  $container.on('submit', '.comment-form', function (e) {
    e.preventDefault();
    const $form = $(this);
    const url = $form.attr('action');
    const formData = new FormData(this);
    const csrftoken = getCsrfToken($form);

    if (!csrftoken) {
      console.error(gettext("CSRF token không tồn tại"));
      alert(gettext("CSRF token missing. Reload page và thử lại."));
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
          // Comment cha
          if (!data.parent_id) {
            let $ul = $container.find('ul.list-unstyled').first();
            if ($ul.length === 0) $ul = $('<ul class="list-unstyled"></ul>').appendTo($container);
            $ul.prepend(data.html);
          } else {
            // Reply
            const $parentComment = $(`#comment-${data.parent_id}`);
            if ($parentComment.length === 0) {
              console.error(gettext("Không tìm thấy comment cha để append reply"));
              return;
            }

            let $replies = $parentComment.find('.replies').first();
            if ($replies.length === 0) {
              const $flexGrow = $parentComment.find('.flex-grow-1').first();
              if (!$flexGrow.length) {
                console.error(gettext("Không tìm thấy container flex-grow-1 để append replies"));
                return;
              }
              $replies = $('<ul class="list-unstyled ms-5 mt-2 replies"></ul>');
              $flexGrow.append($replies);
            }
            $replies.append(data.html);
          }

          // Reset form
          $form[0].reset();
          if ($form.hasClass('reply-form')) $form.addClass('d-none');
        } else {
          console.error(gettext("Lỗi submit:"), data.errors);
          alert(gettext("Có lỗi: ") + JSON.stringify(data.errors));
        }
      },
      error: function (xhr, status, error) {
        console.error(gettext("AJAX Error:"), status, xhr.responseText);
        alert(gettext("Không gửi được comment."));
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
      error: function (xhr, status, error) {
        console.error(gettext("Delete AJAX Error:"), status, xhr.responseText);
        alert(gettext("Không xóa được comment."));
      }
    });
  });
});
