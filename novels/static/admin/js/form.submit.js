(function () {
    window.setupTagFormHandler = function () {
        const $form = $("#tagForm");

        $form.on("submit", function (e) {
            e.preventDefault();
            TagUtils.clearErrors();

            const formData = new FormData(this);
            const action = $form.attr("data-action"); // "edit" hoặc "create"
            const slug = $form.data("slug");           // slug của tag

            const url = action === "edit"
                ? `/novels/admin/tags/${slug}/edit/`
                : `/novels/admin/tags/create/`;

            $.ajax({
                url: url,
                method: "POST",
                headers: {
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                },
                processData: false,
                contentType: false,
                data: formData,
                success: function (data) {
                    if (data.success) {
                        if (action === "create") {
                            fetchTagList(window.currentQuery, 1);
                        } else {
                            fetchTagList(window.currentQuery, window.currentPage);
                        }
                        bootstrap.Modal.getInstance(document.getElementById("tagModal")).hide();
                    } else if (data.errors) {
                        TagUtils.showErrors(data.errors);
                    }
                },
                error: function () {
                    TagUtils.showGeneralError("Đã xảy ra lỗi máy chủ. Vui lòng thử lại sau.");
                }
            });
        });
    };
})();
