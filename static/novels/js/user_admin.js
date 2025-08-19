const rowsPerPage = 10;
const $table = $("#userTable");
const $tbody = $table.find("tbody");
const $pagination = $("#pagination");

let allRows = $tbody.find("tr").toArray(); // lưu toàn bộ rows gốc
let filteredRows = [...allRows];

function showPage(page) {
  const start = (page - 1) * rowsPerPage;
  const end = start + rowsPerPage;

  $(filteredRows).each((index, row) => {
    $(row).toggle(index >= start && index < end);
  });
}

function setupPagination() {
  $pagination.empty();
  const pageCount = Math.ceil(filteredRows.length / rowsPerPage);
  for (let i = 1; i <= pageCount; i++) {
    const $li = $(`
      <li class="page-item">
        <div class="page-link" style="cursor:pointer">${i}</div>
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
  filteredRows = allRows.filter((row) => {
    const text = $(row).text().toLowerCase();
    const match = text.includes(query);
    $(row).toggle(match);
    return match;
  });
  setupPagination();
  showPage(1);
}
$("#novelSearch").on("keyup", filterTable);
setupPagination();
showPage(1);
