$(document).ready(function () {
  $(".toggleChapters").on("click", function (e) {
    e.preventDefault();
    const targetId = $(this).data("target");
    const $extraSection = $("#" + targetId);
    if (!$extraSection.length) return;

    const isHidden = $extraSection.toggleClass("hidden").hasClass("hidden");
    const count = $extraSection.find(".chapter-item").length;

    const showText = $(this).data("text-show");
    const hideText = $(this).data("text-hide");
    const unit = $(this).data("unit");

    $(this).text(isHidden ? `${showText}: (${count} ${unit})` : hideText);
  });
});
