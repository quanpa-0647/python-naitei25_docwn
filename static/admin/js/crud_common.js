$(document).ready(function () {
    function loadTable(query = '') {
        $.get(window.listUrl, { q: query }, function (data) {
            const html = $(data).find("#itemTable").html();
            $("#itemTable").html(html);
        });
    }

    $("#searchInput").on("input", function () {
        loadTable($(this).val());
    });

    $(document).on("click", ".pagination a", function (e) {
        e.preventDefault();
        $.get($(this).attr("href"), function (data) {
            const html = $(data).find("#itemTable").html();
            $("#itemTable").html(html);
        });
    });

    $("#createBtn").click(function () {
        $.get(window.createUrl, function (data) {
            $("#formModal").html(data);
            $("#formModal").modal("show");
        });
    });

    $(document).on("click", ".edit-btn", function () {
        const url = $(this).data("url");
        $.get(url, function (data) {
            $("#formModal").html(data);
            $("#formModal").modal("show");
        });
    });

    $(document).on("submit", "#itemForm", function (e) {
        e.preventDefault();
        const form = $(this);
        $.post(form.attr("action") || window.location.href, form.serialize(), function (data) {
            if (data.success) {
                $("#formModal").modal("hide");
                loadTable();
            } else {
                form.find(".is-invalid").removeClass("is-invalid");
                form.find(".invalid-feedback").remove();

                for (const [field, errors] of Object.entries(data.errors)) {
                    const input = form.find(`[name="${field}"]`);
                    if (input.length) {
                        input.addClass("is-invalid");
                        const feedback = $(`<div class="invalid-feedback">${errors[0]}</div>`);
                        input.after(feedback);
                    }
                }
            }

        });
    });

    let deleteUrl = "";

    $(document).on("click", ".delete-btn", function () {
        deleteUrl = $(this).data("url");
        $("#deleteConfirmModal").modal("show");
    });

    $(document).on("submit", "#deleteForm", function (e) {
        e.preventDefault();
        $.post(deleteUrl, {
            csrfmiddlewaretoken: window.csrfToken
        }, function (data) {
            if (data.success) {
                $("#deleteConfirmModal").modal("hide");
                loadTable();
            }
        });
    });
});
