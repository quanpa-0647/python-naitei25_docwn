$(document).ready(function () {
  const $allCards = $(".like_novel_card");
  const $loadMoreBtn = $("#loadMoreBtn");
  const $collapseBtn = $("#collapseBtn");
  let visibleCount = 6;

  function updateVisibleCards() {
    $allCards.each(function (index) {
      if (index < visibleCount) {
        $(this).removeClass("hidden");
      } else {
        $(this).addClass("hidden");
      }
    });
  }

  $loadMoreBtn.on("click", function (e) {
    e.preventDefault();
    visibleCount += 6;
    updateVisibleCards();

    if (visibleCount >= 18 || visibleCount >= $allCards.length) {
      $loadMoreBtn.hide();
      $collapseBtn
        .css({
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "10px"
        })
        .attr("class", "custom-btn");
    }
  });

  $collapseBtn.on("click", function (e) {
    e.preventDefault();
    visibleCount = 6;
    updateVisibleCards();

    $loadMoreBtn
      .css({
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: "10px"
      })
      .attr("class", "custom-btn")
      .show();

    $collapseBtn.hide();

    window.scrollBy({
      top: -1000,
      behavior: "smooth"
    });
  });

  updateVisibleCards();
});
