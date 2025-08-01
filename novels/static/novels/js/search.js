$(document).ready(function () {
  $("#searchIcon").on("click", function () {
    $(".search-container").toggleClass("active");
    const $input = $("#searchInput");
    if ($input.hasClass("active")) {
      $input.focus();
    }
  });

  $("#searchInput").on("keypress", function (e) {
    if (e.key === "Enter") {
      const query = $(this).val();
      const path = window.location.pathname;

      if (path.includes("/books")) {
        window.location.href = `/books/search/?q=${query}`;
      } else if (path.includes("/users")) {
        window.location.href = `/users/search/?q=${query}`;
      } else {
        window.location.href = `/search/?q=${query}`;
      }
    }
  });
});
