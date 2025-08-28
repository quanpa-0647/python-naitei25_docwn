/* global gettext */
$(document).ready(function() {
    const $toggleBtn = $("#toggle-advanced-search");
    const $advancedFilters = $("#advanced-filters");
    const $filterForm = $('.novel-filter-form');

    // Toggle advanced filters với hiệu ứng slide
    if ($toggleBtn.length && $advancedFilters.length) {
        $toggleBtn.on("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if ($advancedFilters.is(':hidden')) {
                $advancedFilters.slideDown(200);
                $(this).html('<i class="fas fa-filter"></i> ' + gettext("Ẩn tìm kiếm nâng cao"));
            } else {
                $advancedFilters.slideUp(200);
                $(this).html('<i class="fas fa-filter"></i> ' + gettext("Tìm kiếm nâng cao"));
            }
        });
        
        // Check if we have any advanced filters selected and show them
        const hasAdvancedFilters = checkForAdvancedFilters();
        if (hasAdvancedFilters) {
            $advancedFilters.show();
            $toggleBtn.html('<i class="fas fa-filter"></i> ' + gettext("Ẩn tìm kiếm nâng cao"));
        }
    }

    // Auto submit form when sort changes
    const $sortSelect = $('#sort-select');
    if ($sortSelect.length) {
        $sortSelect.on('change', function() {
            // Use the same approach as the submit button
            const form = $(this).closest('form')[0];
            if (form) {
                handleFormSubmission(form);
            }
        });
    }

    // Scroll xuống danh sách novel nếu có query params
    if (window.location.search) {
        const $novelList = $("#novel-list");
        if ($novelList.length) {
            $('html, body').animate({
                scrollTop: $novelList.offset().top - 100
            }, 'smooth');
        }
    }
    
    // Custom form submission handler with parameter preservation
    const $form = $('.novel-filter-form');
    const $submitBtn = $('#filter-submit-btn');
    
    if ($form.length && $submitBtn.length) {
        $submitBtn.on('click', function(e) {
            e.preventDefault();
            handleFormSubmission($form[0]);
        });
    }

    function handleFormSubmission(form) {
        // Get current URL parameters
        const currentUrl = new URL(window.location);
        const currentStatus = currentUrl.searchParams.get('status');
        
        // Create new URL with form data
        const formData = new FormData(form);
        const newUrl = new URL(window.location.pathname, window.location.origin);
        
        // Add form parameters
        for (let [key, value] of formData.entries()) {
            if (value && value.trim()) {
                if (key === 'tags') {
                    // Handle multiple tag values
                    newUrl.searchParams.append(key, value);
                } else {
                    newUrl.searchParams.set(key, value);
                }
            }
        }
        
        // Preserve status if it exists and wasn't in form
        if (currentStatus && !formData.has('status')) {
            newUrl.searchParams.set('status', currentStatus);
        }
        
        // Remove page parameter when filtering
        newUrl.searchParams.delete('page');
        
        // Navigate to new URL
        window.location.href = newUrl.toString();
    }

    function checkForAdvancedFilters() {
        // Check if any tag checkboxes are selected
        const $tagCheckboxes = $('input[name="tags"]:checked');
        if ($tagCheckboxes.length > 0) return true;
        
        // Check if author field has value
        const $authorInput = $('input[name="author"]');
        if ($authorInput.length && $authorInput.val().trim()) return true;
        
        // Check if artist field has value
        const $artistInput = $('input[name="artist"]');
        if ($artistInput.length && $artistInput.val().trim()) return true;
        
        // Check if progress status is selected
        const $progressStatus = $('select[name="progress_status"]');
        if ($progressStatus.length && $progressStatus.val()) return true;
        
        return false;
    }
});
