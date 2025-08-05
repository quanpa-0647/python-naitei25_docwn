/**
 * Chapter Delete functionality
 * Handles confirmation modal and AJAX deletion for user's own chapters
 */

$(document).ready(function() {
    initializeChapterDelete();
});

function initializeChapterDelete() {
    setupDeleteButtons();
    setupDeleteModal();
}

/**
 * Setup delete button event handlers
 */
function setupDeleteButtons() {
    $(document).on('click', '.btn-delete-chapter', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const chapterSlug = $(this).data('chapter-slug');
        const chapterTitle = $(this).data('chapter-title');
        const novelSlug = $(this).data('novel-slug');
        
        if (!chapterSlug || !novelSlug) {
            console.error('Missing chapter or novel slug data');
            return;
        }
        
        showDeleteModal(chapterSlug, chapterTitle, novelSlug);
    });
}

/**
 * Setup modal event handlers
 */
function setupDeleteModal() {
    // Handle modal hidden event to reset form
    $('#deleteChapterModal').on('hidden.bs.modal', function() {
        resetDeleteModal();
    });
}

/**
 * Show delete confirmation modal
 */
function showDeleteModal(chapterSlug, chapterTitle, novelSlug) {
    const modal = $('#deleteChapterModal');
    const titleSpan = $('#deleteChapterTitle');
    const form = $('#deleteChapterForm');
    
    // Set chapter title in modal
    titleSpan.text(chapterTitle);
    
    // Set form action URL
    const deleteUrl = `/novels/${novelSlug}/chapter/${chapterSlug}/delete/`;
    form.attr('action', deleteUrl);
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal[0]);
    modalInstance.show();
}

/**
 * Reset modal content
 */
function resetDeleteModal() {
    $('#deleteChapterTitle').text('');
    $('#deleteChapterForm').attr('action', '');
}

/**
 * Export functions for global access
 */
window.ChapterDelete = {
    showModal: showDeleteModal,
    reset: resetDeleteModal
};
