$(document).ready(function () {
    const $container = $('.finish_novels');
    const $novels = $container.find('.card2-container');
    const $moreCard = $container.find('.more__card');
    const itemsPerPage = 7;
    const totalPages = Math.ceil($novels.length / itemsPerPage);
    const $paginationContainer = $('#pagination');

    $novels.hide();
    $moreCard.hide();
    showPage(1);

    if (totalPages > 1) {
        createPagination();
    }

    function showPage(pageNumber) {
        $novels.hide();
        const startIndex = (pageNumber - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;

        $novels.slice(startIndex, endIndex).show();
        $moreCard.toggle(pageNumber === totalPages);
        updateActivePage(pageNumber);
    }

    function createPagination() {
        $paginationContainer.empty();

        const $prevButton = $('<button>&laquo;</button>').on('click', function () {
            const currentPage = parseInt($('.pagination button.active').text()) || 1;
            if (currentPage > 1) showPage(currentPage - 1);
        });
        $paginationContainer.append($prevButton);

        for (let i = 1; i <= totalPages; i++) {
            const $pageButton = $('<button></button>').text(i);
            if (i === 1) $pageButton.addClass('active');
            $pageButton.on('click', function () {
                showPage(i);
            });
            $paginationContainer.append($pageButton);
        }

        const $nextButton = $('<button>&raquo;</button>').on('click', function () {
            const currentPage = parseInt($('.pagination button.active').text()) || 1;
            if (currentPage < totalPages) showPage(currentPage + 1);
        });
        $paginationContainer.append($nextButton);
    }

    function updateActivePage(pageNumber) {
        $('.pagination button').each(function () {
            $(this).toggleClass('active', $(this).text() === pageNumber.toString());
        });
    }
});
