(function () {
    window.setupTagPagination = function () {
        $(document).on("click", ".page-link", function (e) {
            e.preventDefault();
            const href = $(this).attr("href");
            const url = new URL(href, window.location.origin);
            const page = url.searchParams.get("page");
            if (page) {
                window.currentPage = page;  // lưu lại trang hiện tại
                const query = $("#searchTag").val();
                window.currentQuery = query; 
                fetchTagList(window.currentQuery, page);
            }
        });
    };
})();
