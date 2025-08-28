/* global gettext */

$(document).on("submit", ".report-form", function (e) {
  e.preventDefault();

  const $form = $(this);
  const url = $form.data("url");
  const commentId = $form.data("comment-id");

  // Lấy formData có cả CSRF
  const formData = $form.serialize();

  $.ajax({
    type: "POST",
    url: url,
    data: formData,
    dataType: "json",
    headers: {
      "X-CSRFToken": $form.find("[name=csrfmiddlewaretoken]").val()
    },
    success: function (resp) {
      $("#reportModal" + commentId).modal("hide");
      alert(resp.message || gettext("Báo cáo thành công!"));
      $form.find("button[type=submit]").prop("disabled", true);
    },
    error: function (xhr) {
      if (xhr.status === 400) {
                // lấy message trả về từ view
                let msg = gettext("Bạn đã báo cáo bình luận này rồi.");
                try {
                    msg = JSON.parse(xhr.responseText).error || msg;
                } catch (e) {}
                alert(msg);
            } else {
                alert(gettext("Có lỗi xảy ra. Vui lòng thử lại."));
            }
    }
  });
});
