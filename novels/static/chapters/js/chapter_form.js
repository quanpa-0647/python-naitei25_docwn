// chapter_form.js - JavaScript for chapter form functionality

$(document).ready(function() {
    initializeChapterForm();
});

function initializeChapterForm() {
    initializeVolumeSelection();
    setupChapterFormValidation();
    setupTextareaAutoResize();
}

/**
 * Initialize volume selection functionality for chapter forms
 */
function initializeVolumeSelection() {
    const volumeChoiceSelect = $('#id_volume_choice');
    const newVolumeGroup = $('#new-volume-group');
    const newVolumeInput = $('#id_new_volume_name');
    
    if (volumeChoiceSelect.length && newVolumeGroup.length) {
        // Show/hide new volume name field based on selection
        volumeChoiceSelect.change(function() {
            const selectedValue = $(this).val();
            if (selectedValue === 'new') {
                newVolumeGroup.show();
                newVolumeInput.attr('required', true);
            } else {
                newVolumeGroup.hide();
                newVolumeInput.attr('required', false);
                newVolumeInput.val('');
            }
        });
        
        // Trigger change event on page load to handle form errors
        volumeChoiceSelect.trigger('change');
    }
}

/**
 * Setup chapter form validation
 */
function setupChapterFormValidation() {
    $('#chapter-form').on('submit', function(e) {
        const isValid = validateChapterForm();
        
        if (!isValid) {
            e.preventDefault();
            showChapterValidationErrors();
            return false;
        }
        
        // Show loading state
        showChapterLoadingState();
        return true;
    });
}

/**
 * Validate chapter form fields
 */
function validateChapterForm() {
    let isValid = true;
    const errors = [];

    // Required fields validation
    const titleField = $('#id_title');
    const contentField = $('#id_content');
    const volumeChoiceField = $('#id_volume_choice');
    const newVolumeField = $('#id_new_volume_name');

    // Validate title
    if (!titleField.val() || !titleField.val().trim()) {
        titleField.addClass('error');
        errors.push('Chapter title is required');
        isValid = false;
    } else {
        titleField.removeClass('error');
    }

    // Validate content
    if (!contentField.val() || !contentField.val().trim()) {
        contentField.addClass('error');
        errors.push('Chapter content is required');
        isValid = false;
    } else {
        contentField.removeClass('error');
    }

    // Validate volume selection
    if (!volumeChoiceField.val()) {
        volumeChoiceField.addClass('error');
        errors.push('Please select a volume');
        isValid = false;
    } else {
        volumeChoiceField.removeClass('error');
        
        // If "new" is selected, validate new volume name
        if (volumeChoiceField.val() === 'new') {
            if (!newVolumeField.val() || !newVolumeField.val().trim()) {
                newVolumeField.addClass('error');
                errors.push('New volume name is required');
                isValid = false;
            } else {
                newVolumeField.removeClass('error');
            }
        }
    }

    // Store errors for display
    if (errors.length > 0) {
        sessionStorage.setItem('chapterFormErrors', JSON.stringify(errors));
    }

    return isValid;
}

/**
 * Show chapter form validation errors
 */
function showChapterValidationErrors() {
    const errors = JSON.parse(sessionStorage.getItem('chapterFormErrors') || '[]');
    
    if (errors.length > 0) {
        const errorMessage = 'Please fix the following errors:\n\n' + errors.join('\n');
        alert(errorMessage);
        
        // Focus on first error field
        const firstErrorField = $('.form-input .error').first();
        if (firstErrorField.length) {
            firstErrorField.focus();
            
            // Scroll to field
            $('html, body').animate({
                scrollTop: firstErrorField.closest('.form-group').offset().top - 100
            }, 500);
        }
    }
    
    sessionStorage.removeItem('chapterFormErrors');
}

/**
 * Show loading state during chapter form submission
 */
function showChapterLoadingState() {
    const $form = $('#chapter-form');
    const $submitBtn = $('.submit-btn');
    
    $form.addClass('form-loading');
    $submitBtn.prop('disabled', true).text('Adding Chapter...');
}

/**
 * Setup textarea auto-resize functionality for chapter content
 */
function setupTextareaAutoResize() {
    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 500) + 'px'; // Max height 500px for content
    }

    const contentTextarea = document.getElementById('id_content');
    if (contentTextarea) {
        contentTextarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Initial resize
        autoResize(contentTextarea);
    }

    const titleTextarea = document.getElementById('id_title');
    if (titleTextarea && titleTextarea.tagName.toLowerCase() === 'textarea') {
        titleTextarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Initial resize
        autoResize(titleTextarea);
    }
}

/**
 * Reset error styles on input
 */
$(document).on('input change', 'input, textarea, select', function() {
    $(this).removeClass('error');
});

// Export functions for global access if needed
window.ChapterForm = {
    validate: validateChapterForm,
    initializeVolumeSelection: initializeVolumeSelection
};
