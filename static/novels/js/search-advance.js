$(document).ready(function () {
    $(".search-advance_toggle").on("click", function () {
        $(".search-advance").slideToggle();
    });

    // Giữ mở nếu có filter đã chọn
    let hasFilter =
        $("input[name='author']").val().trim() !== "" ||
        $("input[name='artist']").val().trim() !== "" ||
        $("select[name='status']").val().trim() !== "" ||
        $(".genre_label.active").length > 0;

    if (hasFilter) {
        $(".search-advance").show();
    }
});
