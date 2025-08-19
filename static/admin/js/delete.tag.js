(function () {
    window.setupTagDeleteHandler = function () {
        let currentTagSlugToDelete = null;

        function getDeleteModalInstance() {
            const modalEl = document.getElementById("deleteConfirmModal");
            if (!modalEl) return null;
            return bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        }

        // Gắn sự kiện khi nhấn nút "Xóa"
        $(document).on("click", ".delete-btn", function () {
            const $row = $(this).closest("tr");
            currentTagSlugToDelete = $row.data("slug");
            getDeleteModalInstance().show();
        });

        // Gắn sự kiện xác nhận xóa
        $(document).on("click", "#confirmDeleteBtn", function () {
            if (!currentTagSlugToDelete) return;

            const tagSlugToDelete = currentTagSlugToDelete; // Lưu lại giá trị tạm thời
            currentTagSlugToDelete = null;

            const modalInstance = getDeleteModalInstance();
            if (modalInstance) {
                modalInstance.hide();
            }

            $.ajax({
                url: `/admin/tags/${tagSlugToDelete}/delete/`,
                method: "POST",
                headers: {
                    "X-CSRFToken": $("#csrfToken").val(),
                },
                success: function (data) {
                    if (data.success) {
                        getDeleteModalInstance().hide();
                        // Đếm số tag hiện tại trên trang (trước khi reload)
                        const rowCount = $("#tagTableBody tr").length;

                        if (rowCount === 1 && window.currentPage > 1) {
                            // Nếu tag bị xóa là tag cuối cùng của trang và không phải trang đầu
                            window.currentPage -= 1;
                        }

                        fetchTagList(window.currentQuery, window.currentPage);

                    } else {
                        TagUtils.showGeneralError("Không thể xóa tag.");
                    }
                },
                error: function () {
                    TagUtils.showGeneralError("Đã xảy ra lỗi khi xóa.");
                }
            });
        });
    };
})();
