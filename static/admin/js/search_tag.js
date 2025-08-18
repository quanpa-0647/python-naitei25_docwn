(function () {
    window.setupTagSearch = function () {
        const $searchInput = $("#searchTag");
        let debounceTimer = null;

        $searchInput.on("input", function () {
            clearTimeout(debounceTimer);
            const query = $(this).val();
            window.currentQuery = query;   // lưu lại query hiện tại
            window.currentPage = 1;        // reset về page 1
            fetchTagList(query, 1);

            debounceTimer = setTimeout(() => {
                fetchTagList(query, 1);
            }, 500);
        });
    };
})();
