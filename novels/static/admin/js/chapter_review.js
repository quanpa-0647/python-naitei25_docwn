class ChapterReview {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.initializeFeatures();
    }

    initializeElements() {
        this.textarea = document.getElementById('rejected_reason');
        this.approveBtn = document.querySelector('button[value="approve"]');
        this.rejectBtn = document.querySelector('button[value="reject"]');
        this.form = document.querySelector('form');
        this.contentArea = document.querySelector('.prose');
    }

    bindEvents() {
        // Auto-resize textarea
        if (this.textarea) {
            this.textarea.addEventListener('input', this.handleTextareaResize.bind(this));
            this.textarea.addEventListener('focus', this.handleTextareaFocus.bind(this));
            this.textarea.addEventListener('blur', this.handleTextareaBlur.bind(this));
        }

        // Button confirmations
        if (this.approveBtn) {
            this.approveBtn.addEventListener('click', this.handleApprove.bind(this));
        }

        if (this.rejectBtn) {
            this.rejectBtn.addEventListener('click', this.handleReject.bind(this));
        }

        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Auto-save draft
        if (this.textarea) {
            this.textarea.addEventListener('input', this.debounce(this.saveDraft.bind(this), 1000));
        }
    }

    initializeFeatures() {
        this.initializeTooltips();
        this.initializeReadingProgress();
        this.loadDraft();
        this.initializeWordCount();
    }

    handleTextareaResize() {
        this.textarea.style.height = 'auto';
        this.textarea.style.height = this.textarea.scrollHeight + 'px';
    }

    handleTextareaFocus() {
        this.textarea.classList.add('ring-2', 'ring-blue-500');
    }

    handleTextareaBlur() {
        this.textarea.classList.remove('ring-2', 'ring-blue-500');
    }

    handleApprove(e) {
        const confirmed = this.showConfirmDialog({
            title: window.translations?.confirmApprove,
            message: window.translations?.confirmApproveMessage,
            confirmText: window.translations?.approve,
            confirmClass: 'btn-approve',
            icon: 'check-circle'
        });

        if (!confirmed) {
            e.preventDefault();
        } else {
            this.showLoadingState(e.target);
        }
    }

    handleReject(e) {
        const reason = this.textarea?.value.trim();
        
        if (!reason) {
            this.showAlert('error', window.translations?.reasonRequired);
            e.preventDefault();
            this.textarea?.focus();
            return;
        }

        const confirmed = this.showConfirmDialog({
            title: window.translations?.confirmReject,
            message: window.translations?.confirmRejectMessage,
            confirmText: window.translations?.reject,
            confirmClass: 'btn-reject',
            icon: 'times-circle'
        });

        if (!confirmed) {
            e.preventDefault();
        } else {
            this.showLoadingState(e.target);
        }
    }

    handleFormSubmit(e) {
        const submitBtn = e.submitter;
        if (submitBtn) {
            this.showLoadingState(submitBtn);
            this.clearDraft();
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter to approve
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (this.approveBtn && !this.approveBtn.disabled) {
                this.approveBtn.click();
            }
        }

        // Escape to clear textarea
        if (e.key === 'Escape' && this.textarea === document.activeElement) {
            this.textarea.value = '';
            this.textarea.blur();
            this.handleTextareaResize();
        }
    }

    showConfirmDialog({ title, message, confirmText, confirmClass, icon }) {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'confirm-dialog';
        
        overlay.innerHTML = `
            <div class="confirm-content">
                <div class="flex items-center gap-3 mb-4">
                    <i class="fas fa-${icon} text-2xl text-gray-600"></i>
                    <h3 class="confirm-title">${title}</h3>
                </div>
                <p class="confirm-message">${message}</p>
                <div class="confirm-actions">
                    <button type="button" class="btn-nav btn-nav-secondary cancel-btn">
                        ${window.translations?.cancel}
                    </button>
                    <button type="button" class="${confirmClass} confirm-btn">
                        ${confirmText}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        return new Promise((resolve) => {
            const confirmBtn = overlay.querySelector('.confirm-btn');
            const cancelBtn = overlay.querySelector('.cancel-btn');

            const cleanup = () => {
                document.body.removeChild(overlay);
            };

            confirmBtn.addEventListener('click', () => {
                cleanup();
                resolve(true);
            });

            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    cleanup();
                    resolve(false);
                }
            });

            // Focus the cancel button by default
            cancelBtn.focus();
        });
    }

    showLoadingState(button) {
        button.disabled = true;
        button.classList.add('loading');
        
        const originalText = button.innerHTML;
        button.innerHTML = `
            <i class="fas fa-spinner fa-spin mr-2"></i>
            ${window.translations?.processing || 'Processing...'}
        `;

        // Restore button after 30 seconds (fallback)
        setTimeout(() => {
            button.disabled = false;
            button.classList.remove('loading');
            button.innerHTML = originalText;
        }, 30000);
    }

    showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-md`;
        alertContainer.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas fa-${this.getAlertIcon(type)}"></i>
                <span>${message}</span>
                <button type="button" class="ml-auto" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(alertContainer);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentElement) {
                alertContainer.remove();
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[title]');
        tooltipElements.forEach(element => {
            let tooltip;

            element.addEventListener('mouseenter', () => {
                tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = element.getAttribute('title');
                document.body.appendChild(tooltip);

                const rect = element.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';

                setTimeout(() => tooltip.classList.add('show'), 10);
            });

            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                }
            });

            // Remove title to prevent default tooltip
            element.removeAttribute('title');
            element.setAttribute('data-title', element.getAttribute('title') || '');
        });
    }

    initializeReadingProgress() {
        if (!this.contentArea) return;

        const progressBar = document.createElement('div');
        progressBar.className = 'fixed top-0 left-0 w-full h-1 bg-blue-500 z-50 transform scale-x-0 origin-left transition-transform duration-300';
        document.body.appendChild(progressBar);

        const updateProgress = () => {
            const scrollTop = window.pageYOffset;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = scrollTop / docHeight;
            
            progressBar.style.transform = `scaleX(${Math.min(progress, 1)})`;
        };

        window.addEventListener('scroll', this.throttle(updateProgress, 16));
    }

    saveDraft() {
        if (this.textarea && this.textarea.value.trim()) {
            localStorage.setItem('chapter_rejection_draft', this.textarea.value);
        }
    }

    loadDraft() {
        const draft = localStorage.getItem('chapter_rejection_draft');
        if (draft && this.textarea && !this.textarea.value) {
            this.textarea.value = draft;
            this.handleTextareaResize();
        }
    }

    clearDraft() {
        localStorage.removeItem('chapter_rejection_draft');
    }

    initializeWordCount() {
        if (!this.textarea) return;

        const counter = document.createElement('div');
        counter.className = 'text-sm text-gray-500 mt-2';
        counter.id = 'word-counter';
        this.textarea.parentNode.appendChild(counter);

        const updateCounter = () => {
            const text = this.textarea.value;
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            const chars = text.length;
            
            counter.textContent = `${chars} characters, ${words} words`;
        };

        this.textarea.addEventListener('input', updateCounter);
        updateCounter();
    }

    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChapterReview();
});
