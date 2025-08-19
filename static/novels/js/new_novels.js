$(document).ready(function () {
    const $container = $('#new_novels');
    const $novels = $container.find('.card2-container');
    const $moreCard = $container.find('.more__card');
    const itemsPerPage = 16;
    const totalPages = Math.ceil($novels.length / itemsPerPage);
    const $paginationContainer = $('#pagination');
  
    if ($novels.length <= itemsPerPage) {
      $novels.show();
      $moreCard.show();
      return;
    }
  
    $novels.hide();
    $moreCard.hide();
  
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
  
      // Previous button
      const $prevButton = $('<button>&laquo;</button>');
      $prevButton.on('click', function () {
        const currentPage = parseInt($paginationContainer.find('button.active').text()) || 1;
        if (currentPage > 1) showPage(currentPage - 1);
      });
      $paginationContainer.append($prevButton);
  
      // Page number buttons
      for (let i = 1; i <= totalPages; i++) {
        const $pageButton = $('<button></button>').text(i);
        if (i === 1) $pageButton.addClass('active');
        $pageButton.on('click', function () {
          showPage(i);
        });
        $paginationContainer.append($pageButton);
      }
  
      // Next button
      const $nextButton = $('<button>&raquo;</button>');
      $nextButton.on('click', function () {
        const currentPage = parseInt($paginationContainer.find('button.active').text()) || 1;
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
  
