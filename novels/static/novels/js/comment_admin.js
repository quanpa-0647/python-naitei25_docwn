const rowsPerPage = 10;
const $table = $("#commentTable");
const $tbody = $table.find("tbody");
const $allRows = $tbody.find("tr");
const $pagination = $("#pagination");
let $filteredRows = $allRows;

function showPage(page) {
  const start = (page - 1) * rowsPerPage;
  const end = start + rowsPerPage;

  $filteredRows.each(function (index) {
    $(this).toggle(index >= start && index < end);
  });
}

function setupPagination() {
  $pagination.empty();
  const pageCount = Math.ceil($filteredRows.length / rowsPerPage);

  for (let i = 1; i <= pageCount; i++) {
    const $li = $(`
      <li class="page-item">
        <button class="page-link">${i}</button>
      </li>
    `);

    $li.on("click", function () {
      showPage(i);
      $pagination.find(".page-item").removeClass("active");
      $(this).addClass("active");
    });

    $pagination.append($li);
  }

  if (pageCount > 0) {
    $pagination.children().first().addClass("active");
  }
}

function filterTable() {
  const query = $("#novelSearch").val().toLowerCase();

  $filteredRows = $allRows.filter(function () {
    const text = $(this).text().toLowerCase();
    const match = text.includes(query);
    $(this).toggle(match);
    return match;
  });

  setupPagination();
  showPage(1);
}

// Khởi tạo ban đầu
setupPagination();
showPage(1);
