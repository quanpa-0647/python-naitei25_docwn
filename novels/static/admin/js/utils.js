(function () {
    window.fetchTagList = function (query = "", page = 1) {
        window.currentQuery = query;
        window.currentPage = page;

        const $wrapper = $("#tagTableWrapper");
        $.ajax({
            url: `/novels/admin/tags/?q=${encodeURIComponent(query)}&page=${page}`,
            headers: { "X-Requested-With": "XMLHttpRequest" },
            success: function (html) {
                $wrapper.html(html);

                const rowCount = $("#tagTableBody tr").length;
                if (rowCount === 0 && page > 1) {
                    return fetchTagList(query, page - 1);
                }

                setupTagDeleteHandler();
                setupTagPagination();
            }
        });
    };


    window.TagUtils = {
        clearErrors: function () {
            const $form = $("#tagForm");
            $form.find("[name='name']").removeClass("is-invalid");
            $form.find("[name='description']").removeClass("is-invalid");
            $form.find(".name-error").text("");
            $form.find(".description-error").text("");
            $("#general-error").addClass("d-none").text("");
        },

        showErrors: function (errors) {
            const $form = $("#tagForm");
            if (errors.name) {
                const error = errors.name[0];
                $form.find("[name='name']").addClass("is-invalid");
                $form.find(".name-error").text(typeof error === "string" ? error : error.message);
            }
            if (errors.description) {
                const error = errors.description[0];
                $form.find("[name='description']").addClass("is-invalid");
                $form.find(".description-error").text(typeof error === "string" ? error : error.message);
            }
        },

        showGeneralError: function (msg) {
            $("#general-error").removeClass("d-none").text(msg);
            $("html, body").animate({ scrollTop: 0 }, "smooth");
        }
    };
})();
