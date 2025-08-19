(function () {
    window.setupTagModalHandler = function () {
        const $form = $("#tagForm");
        const $tagSlugInput = $form.find("input[name='tag_slug']");
        const $name = $form.find("[name='name']");
        const $desc = $form.find("[name='description']");

        $("#tagModal").on("show.bs.modal", function (event) {
            const $button = $(event.relatedTarget);
            const action = $button.data("action");

            $form[0].reset();
            TagUtils.clearErrors();

            $form.attr("data-action", action);

            if (action === "edit") {
                const $row = $button.closest("tr");
                $form.data("slug", $row.data("slug"));
                $form.find("input[name='tag_slug']").val($row.data("slug"));
                $name.val($row.find(".tag-name").text().trim());
                $desc.val($row.find(".tag-desc").text().trim());
            } else {
                $form.data("slug", "");
                $tagSlugInput.val("");
            }
        });
    };
})();
