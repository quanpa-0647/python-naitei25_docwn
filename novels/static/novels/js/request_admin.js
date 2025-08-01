function setupTableSearchAndPagination(tableId, searchId, paginationId) {
  const rowsPerPage = 10;
  const $table = $("#" + tableId);
  const $tbody = $table.find("tbody");
  const $allRows = $tbody.find("tr");
  const $pagination = $("#" + paginationId);
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
          <div class="page-link" style="cursor:pointer">${i}</div>
        </li>
      `);
      $li.on("click", function () {
        showPage(i);
        $pagination.find(".page-item").removeClass("active");
        $li.addClass("active");
      });
      $pagination.append($li);
    }
    if (pageCount > 0) {
      $pagination.children().first().addClass("active");
    }
  }
  function filterTable() {
    const query = $("#" + searchId).val().toLowerCase();
    $filteredRows = $allRows.filter(function () {
      const text = $(this).text().toLowerCase();
      const match = text.includes(query);
      $(this).toggle(match);
      return match;
    });
    setupPagination();
    showPage(1);
  }
  $("#" + searchId).on("keyup", filterTable);
  setupPagination();
  showPage(1);
}
$(document).ready(function () {
  setupTableSearchAndPagination("tableNovel", "searchNovel", "paginationNovel");
  setupTableSearchAndPagination("tableVol", "searchVol", "paginationVol");
  setupTableSearchAndPagination("tableChap", "searchChap", "paginationChap");
});
