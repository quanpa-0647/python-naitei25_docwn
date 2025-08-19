$(document).ready(function () {
  const $novels = $('#novelsWrapper .card1');
  const itemsPerPage = 12;
  const totalPages = Math.ceil($novels.length / itemsPerPage);
  const $paginationContainer = $('#pagination');

  $novels.hide(); // Ẩn tất cả ban đầu
  showPage(1);
  createPagination();

  function showPage(pageNumber) {
    $novels.hide(); // Ẩn tất cả

    const startIndex = (pageNumber - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;

    $novels.slice(startIndex, endIndex).show(); // Hiển thị các phần tử cần thiết
    updateActivePage(pageNumber);
  }

  function createPagination() {
    $paginationContainer.empty();

    // Nút Previous
    const $prevButton = $('<button>&laquo;</button>');
    $prevButton.on('click', function () {
      const currentPage = parseInt($paginationContainer.find('button.active').text()) || 1;
      if (currentPage > 1) {
        showPage(currentPage - 1);
      }
    });
    $paginationContainer.append($prevButton);

    // Các nút số trang
    for (let i = 1; i <= totalPages; i++) {
      const $pageButton = $('<button></button>').text(i);
      if (i === 1) $pageButton.addClass('active');
      $pageButton.on('click', function () {
        showPage(i);
      });
      $paginationContainer.append($pageButton);
    }

    // Nút Next
    const $nextButton = $('<button>&raquo;</button>');
    $nextButton.on('click', function () {
      const currentPage = parseInt($paginationContainer.find('button.active').text()) || 1;
      if (currentPage < totalPages) {
        showPage(currentPage + 1);
      }
    });
    $paginationContainer.append($nextButton);
  }

  function updateActivePage(currentPage) {
    $paginationContainer.find('button').removeClass('active');
    $paginationContainer.find('button').each(function () {
      if ($(this).text() === currentPage.toString()) {
        $(this).addClass('active');
      }
    });
  }
});


