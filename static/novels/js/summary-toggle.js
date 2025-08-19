$(document).ready(function () {
  const $summary = $("#summary");
  const $summaryToggleBtn = $("#toggleSummary");

  if ($summary.length && $summaryToggleBtn.length) {
    const originalHeight = $summary[0].scrollHeight;
    if (originalHeight <= 60) {
      $summaryToggleBtn.hide();
      $summary.removeClass("short");
    }

    const showText = $summaryToggleBtn.data("text-show");
    const hideText = $summaryToggleBtn.data("text-hide");

    $summaryToggleBtn.on("click", function () {
      $summary.toggleClass("short");
      $(this).text($summary.hasClass("short") ? showText : hideText);
    });
  }
});
