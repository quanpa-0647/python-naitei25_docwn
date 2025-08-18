$(document).ready(function () {
    const currentPageFromDOM = $("#tagTableWrapper").data("current-page");
    window.currentPage = currentPageFromDOM || 1;
    window.currentQuery = $("#searchTag").val() || ""

    setupTagModalHandler();
    setupTagFormHandler();
    setupTagDeleteHandler();
    setupTagSearch();
    setupTagPagination();
});
