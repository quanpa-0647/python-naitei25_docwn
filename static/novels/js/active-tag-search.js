const searchForm = document.querySelector("#search-form");

if (searchForm) {
    // toggle chọn/un-chọn tag
    document.querySelectorAll('.genre_label').forEach(label => {
        label.addEventListener('click', () => {
            const slug = label.dataset.genreSlug;
            label.classList.toggle("active");

            const icon = label.querySelector("i");
            if (label.classList.contains("active")) {
                icon.classList.remove("fa-square");
                icon.classList.add("fa-check-square");
            } else {
                icon.classList.remove("fa-check-square");
                icon.classList.add("fa-square");
            }
        });
    });

    searchForm.addEventListener("submit", function () {
        // xóa input tags cũ
        this.querySelectorAll("input[name='tags']").forEach(el => el.remove());

        // gom slug các tag đã chọn
        const activeGenres = [...document.querySelectorAll('.genre_label.active')]
            .map(label => label.dataset.genreSlug);

        // tạo input hidden cho mỗi slug
        activeGenres.forEach(slug => {
            const hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "tags";
            hiddenInput.value = slug;
            this.appendChild(hiddenInput);
        });
    });
}
