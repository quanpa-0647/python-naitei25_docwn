document.addEventListener("DOMContentLoaded", function() {
    const toggleBtn = document.getElementById("toggle-advanced-search");
    const advancedFilters = document.getElementById("advanced-filters");

    // Toggle advanced filters với hiệu ứng slide
    if (toggleBtn && advancedFilters) {
        toggleBtn.addEventListener("click", function() {
            if (advancedFilters.style.display === "none" || advancedFilters.style.display === "") {
                $(advancedFilters).slideDown(200);
            } else {
                $(advancedFilters).slideUp(200);
            }
        });
    }

    // Scroll xuống danh sách novel nếu có query params
    if (window.location.search) {
        const novelList = document.getElementById("novel-list");
        if (novelList) {
            window.scrollTo({
                top: novelList.offsetTop - 100, // offset có thể điều chỉnh
                behavior: "smooth"
            });
        }
    }
});
