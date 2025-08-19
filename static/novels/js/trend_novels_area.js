function switchPage(pageNum) {
  const pages = $(".trend_novels_page");
  const dots = $(".dot");

  pages.each(function(index) {
    if (index === pageNum - 1) {
      $(this).addClass("active").css("display", "flex");
    } else {
      $(this).removeClass("active").css("display", "none");
    }
  });

  dots.each(function(index) {
    $(this).toggleClass("active", index === pageNum - 1);
  });
}

$(document).ready(function () {
  switchPage(1);
});
