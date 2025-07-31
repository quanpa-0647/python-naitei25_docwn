$(document).ready(function () {
  const $openTOC = $("#openTOC");
  const $closeTOC = $("#closeTOC");
  const $tocOverlay = $("#tocOverlay");
  const $tocBox = $(".toc-box");

  if ($openTOC.length && $closeTOC.length && $tocOverlay.length) {
    $openTOC.on("click", function (e) {
      e.preventDefault();
      $tocOverlay.addClass("show");
    });

    $closeTOC.on("click", function () {
      $tocOverlay.removeClass("show");
    });

    $(".toc-list a").on("click", function (e) {
      e.preventDefault();
      const targetId = $(this).attr("href").substring(1);
      const $targetEl = $("#" + targetId);
      if ($targetEl.length) {
        $targetEl[0].scrollIntoView({ behavior: "smooth" });
      }
    });

    $(document).on("click", function (e) {
      if (
        !$tocOverlay.is(e.target) &&
        $tocOverlay.has(e.target).length === 0 &&
        !$openTOC.is(e.target)
      ) {
        $tocOverlay.removeClass("show");
      }
    });

    $tocBox.on("click", function (e) {
      e.stopPropagation();
    });
  }
});
