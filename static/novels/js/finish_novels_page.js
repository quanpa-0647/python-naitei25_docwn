$(document).ready(function () {
    const $container = $('#finish_novels');
    const $novels = $container.find('.card2-container');
    const $moreCard = $container.find('.more__card');
    const itemsPerPage = 12;
    const totalPages = Math.ceil($novels.length / itemsPerPage);
    const $paginationContainer = $('#pagination');

    // Nếu ít hơn 1 trang thì hiển thị tất cả
    if ($novels.length <= itemsPerPage) {
        $novels.show();
        if ($moreCard.length) $moreCard.show();
        return;
    }

    $novels.hide();
    if ($moreCard.length) $moreCard.hide();

    showPage(1);
    createPagination();

    function showPage(pageNumber) {
        $novels.hide();

        const startIndex = (pageNumber - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;

        $novels.slice(startIndex, endIndex).show();

        if ($moreCard.length) {
            $moreCard.toggle(pageNumber === totalPages);
        }

        updateActivePage(pageNumber);
    }

    function createPagination() {
        $paginationContainer.empty();

        // Nút Previous
        const $prevButton = $('<button>').html('&laquo;');
        $prevButton.on('click', function () {
            const $active = $paginationContainer.find('button.active');
            const currentPage = parseInt($active.text()) || 1;
            if (currentPage > 1) showPage(currentPage - 1);
        });
        $paginationContainer.append($prevButton);

        // Các nút số trang
        for (let i = 1; i <= totalPages; i++) {
            const $pageButton = $('<button>').text(i);
            if (i === 1) $pageButton.addClass('active');
            $pageButton.on('click', function () {
                showPage(i);
            });
            $paginationContainer.append($pageButton);
        }

        // Nút Next
        const $nextButton = $('<button>').html('&raquo;');
        $nextButton.on('click', function () {
            const $active = $paginationContainer.find('button.active');
            const currentPage = parseInt($active.text()) || 1;
            if (currentPage < totalPages) showPage(currentPage + 1);
        });
        $paginationContainer.append($nextButton);
    }

    function updateActivePage(pageNumber) {
        $paginationContainer.find('button').removeClass('active');
        $paginationContainer.find('button').each(function () {
            if ($(this).text() === pageNumber.toString()) {
                $(this).addClass('active');
            }
        });
    }
});
