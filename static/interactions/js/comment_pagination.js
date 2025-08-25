$(document).ready(function () {
    const container = $("#comment-container");
    const commentsUrl = container.data("url"); // URL từ data-url

    function loadComments(page = 1) {
        $.ajax({
            url: `${commentsUrl}?page=${page}`,
            type: "GET",
            success: function (data) {
                container.html(data.html);
            },
            error: function (xhr) {
                console.error("Error loading comments:", xhr);
            }
        });
    }

    // Lần đầu load
    loadComments();

    // Bắt sự kiện phân trang (match class trong template)
    $(document).on("click", ".paging_item[data-page]:not(.disabled)", function (e) {
        e.preventDefault();
        const page = $(this).data("page");

        if ($(this).hasClass("disabled") || !page) {
        return;
        }
        
        if (page) {
            loadComments(page);
        }
    });
});
