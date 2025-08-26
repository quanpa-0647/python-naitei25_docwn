class NovelReviews {
    constructor(novelSlug) {
        this.novelSlug = novelSlug;
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.currentFilters = {
            rating: '',
            sort: '-created_at'
        };
        this.currentUser = window.currentUser || null;
        this.isAdmin = window.isAdmin || false;
        this.userHasReviewed = window.userHasReviewed || false;
        this.isSubmittingReview = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadReviews(true);
    }
    
    bindEvents() {
        // Rating filter change
        $('#rating-filter').on('change', (e) => {
            this.currentFilters.rating = e.target.value;
            this.resetAndLoad();
        });
        
        // Sort filter change
        $('#sort-filter').on('change', (e) => {
            this.currentFilters.sort = e.target.value;
            this.resetAndLoad();
        });
        
        // Load more button
        $('#load-more-reviews').on('click', () => {
            this.loadMoreReviews();
        });

        // Add review button
        $('#add-review-btn').on('click', (e) => {
            e.preventDefault();
            if (!$(e.target).is(':disabled')) {
                this.showAddReviewForm();
            }
        });

        // Cancel add review form
        $(document).on('click', '.cancel-form-btn', (e) => {
            e.preventDefault();
            this.hideAddReviewForm();
        });

        // Submit new review
        $('#review-form').on('submit', (e) => {
            e.preventDefault();
            this.submitNewReview();
        });

        // Character counter for new review
        $('#review-content').on('input', (e) => {
            const length = e.target.value.length;
            $('#char-count').text(length);
            
            if (length > 2000) {
                $('#char-count').addClass('over-limit');
            } else {
                $('#char-count').removeClass('over-limit');
            }
        });

        // Delegate events for dynamically created elements
        $(document).on('click', '.edit-review-btn', (e) => {
            e.preventDefault();
            const reviewId = $(e.target).closest('.review-item').data('review-id');
            this.editReview(reviewId);
        });

        $(document).on('click', '.delete-review-btn', (e) => {
            e.preventDefault();
            const reviewId = $(e.target).closest('.review-item').data('review-id');
            this.deleteReview(reviewId);
        });

        $(document).on('click', '.user-profile-link', (e) => {
            e.preventDefault();
            const username = $(e.target).closest('.user-profile-link').data('username');
            window.location.href = `/accounts/profile/${username}/`;
        });

        // Cancel edit
        $(document).on('click', '.cancel-edit-btn', (e) => {
            e.preventDefault();
            const reviewId = $(e.target).closest('.review-item').data('review-id');
            this.cancelEdit(reviewId);
        });

        // Save edit
        $(document).on('click', '.save-edit-btn', (e) => {
            e.preventDefault();
            const reviewId = $(e.target).closest('.review-item').data('review-id');
            this.saveEdit(reviewId);
        });
    }

    showAddReviewForm() {
        $('#add-review-form').slideDown(300);
        $('#add-review-btn').prop('disabled', true).addClass('disabled');
        $('#review-content').focus();
        
        // Scroll to form
        $('html, body').animate({
            scrollTop: $('#add-review-form').offset().top - 20
        }, 300);
    }

    hideAddReviewForm() {
        $('#add-review-form').slideUp(300);
        $('#add-review-btn').prop('disabled', false).removeClass('disabled');
        
        // Reset form
        $('#review-form')[0].reset();
        $('#char-count').text('0').removeClass('over-limit');
    }

    async submitNewReview() {
        if (this.isSubmittingReview) return;
        
        const rating = $('#review-rating').val();
        const content = $('#review-content').val().trim();
        
        // Validation
        if (!rating) {
            this.showMessage(gettext('Vui lòng chọn số sao đánh giá.'), 'error');
            return;
        }
        
        if (!content) {
            this.showMessage(gettext('Vui lòng nhập nội dung đánh giá.'), 'error');
            return;
        }
        
        if (content.length > 2000) {
            this.showMessage(gettext('Nội dung đánh giá không được vượt quá 2000 ký tự.'), 'error');
            return;
        }

        this.isSubmittingReview = true;
        const submitBtn = $('#review-form button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true).html(`
            <div class="loading-spinner" style="width: 12px; height: 12px; margin-right: 6px; display: inline-block;"></div>
            ${gettext('Đang đăng...')}
        `);

        try {
            const response = await fetch(`/interactions/ajax/${this.novelSlug}/reviews/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: new URLSearchParams({
                    rating: rating,
                    content: content
                })
            });

            const data = await response.json();

            if (data.success) {
                // Hide form
                this.hideAddReviewForm();
                
                // Mark user as reviewed
                this.userHasReviewed = true;
                $('#add-review-btn')
                    .prop('disabled', true)
                    .attr('title', gettext('Bạn đã đánh giá cuốn tiểu thuyết này rồi'));
                
                // Add new review to the top of the list
                const newReviewHtml = this.renderReview(data.review);
                $('#reviews-list').prepend(newReviewHtml);
                
                // Update review count
                const currentCount = parseInt($('.review-count').text().replace(/[()]/g, ''));
                $('.review-count').text(`(${currentCount + 1})`);
                
                // Hide empty state if it was showing
                $('.reviews-empty').hide();
                $('.reviews-list').show();
                
                // Show success message
                this.showMessage(data.message, 'success');
                
                // Highlight new review
                const newReview = $(`.review-item[data-review-id="${data.review.id}"]`);
                newReview.addClass('new-review');
                setTimeout(() => {
                    newReview.removeClass('new-review');
                }, 3000);
                
            } else {
                this.showMessage(data.message || gettext('Có lỗi xảy ra khi đăng đánh giá.'), 'error');
                
                // Handle specific case where user already reviewed
                if (data.message && data.message.includes('đã đánh giá')) {
                    this.userHasReviewed = true;
                    $('#add-review-btn')
                        .prop('disabled', true)
                        .attr('title', gettext('Bạn đã đánh giá cuốn tiểu thuyết này rồi'));
                    this.hideAddReviewForm();
                }
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            this.showMessage(gettext('Có lỗi xảy ra khi đăng đánh giá.'), 'error');
        } finally {
            this.isSubmittingReview = false;
            submitBtn.prop('disabled', false).html(originalText);
        }
    }
    
    resetAndLoad() {
        this.currentPage = 1;
        this.hasMore = true;
        $('#reviews-list').empty();
        $('.load-more-container').hide();
        $('.reviews-empty').hide();
        this.loadReviews(true);
    }
    
    async loadReviews(isInitial = false) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(isInitial);
        
        try {
            const response = await fetch(this.buildUrl());
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.renderReviews(data, isInitial);
            
        } catch (error) {
            console.error('Error loading reviews:', error);
            this.showError();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMoreReviews() {
        if (!this.hasMore || this.isLoading) return;
        
        this.currentPage++;
        await this.loadReviews();
    }
    
    buildUrl() {
        const params = new URLSearchParams({
            page: this.currentPage,
            rating: this.currentFilters.rating,
            sort: this.currentFilters.sort
        });
        
        return `/interactions/ajax/${this.novelSlug}/reviews/?${params.toString()}`;
    }
    
    showLoading(isInitial) {
        if (isInitial) {
            $('.reviews-loading').show();
        } else {
            $('#load-more-reviews').prop('disabled', true).html(`
                <div class="loading-spinner" style="width: 12px; height: 12px; margin-right: 6px; display: inline-block;"></div>
                ${gettext('Đang tải...')}
            `);
        }
    }
    
    hideLoading() {
        $('.reviews-loading').hide();
        $('#load-more-reviews').prop('disabled', false).html(`
            <i class="fas fa-chevron-down"></i>
            ${gettext('Tải thêm đánh giá')}
        `);
    }
    
    renderReviews(data, isInitial) {
        const reviewsHtml = data.reviews.map(review => this.renderReview(review)).join('');
        
        if (isInitial) {
            $('#reviews-list').html(reviewsHtml);
        } else {
            $('#reviews-list').append(reviewsHtml);
        }
        
        // Update pagination state
        this.hasMore = data.has_next;
        
        if (this.hasMore) {
            $('.load-more-container').show();
        } else {
            $('.load-more-container').hide();
        }
        
        // Show empty state if no reviews
        if (data.reviews.length === 0 && isInitial) {
            $('.reviews-list').hide();
            $('.reviews-empty').show();
        } else {
            $('.reviews-empty').hide();
            $('.reviews-list').show();
        }
        
        // Update review count
        $('.review-count').text(`(${data.total_reviews})`);
    }
    
    renderReview(review) {
        const starsHtml = this.renderStars(review.rating);
        const canModify = this.canUserModifyReview(review);
        const actionButtonsHtml = canModify ? this.renderActionButtons(review) : '';
        
        return `
            <div class="review-item" data-review-id="${review.id}">
                <div class="review-header">
                    <div class="review-user">
                        <div class="user-profile-link" data-username="${review.user.username}" style="display: flex; align-items: center; cursor: pointer;">
                            <div class="user-avatar" style="background-image: url('${review.user.avatar_url}');"></div>
                            <div class="user-info">
                                <h4 class="username-link">${this.escapeHtml(review.user.username)}</h4>
                                <div class="review-date">${this.formatDate(review.created_at)}</div>
                            </div>
                        </div>
                    </div>
                    <div class="review-rating-actions">
                        <div class="review-rating">
                            ${starsHtml}
                        </div>
                        ${actionButtonsHtml}
                    </div>
                </div>
                <div class="review-content">
                    <div class="review-content-display">
                        ${this.formatContent(review.content)}
                    </div>
                    <div class="review-content-edit" style="display: none;">
                        <div class="edit-rating" style="margin-bottom: 10px;">
                            <label>${gettext('Đánh giá:')}</label>
                            <select class="edit-rating-select" style="margin-left: 8px;">
                                ${this.renderRatingOptions(review.rating)}
                            </select>
                        </div>
                        <textarea class="edit-content-textarea" style="width: 100%; min-height: 100px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">${this.escapeHtml(review.content)}</textarea>
                        <div class="edit-actions" style="margin-top: 10px;">
                            <button class="save-edit-btn btn btn-primary btn-sm">
                                <i class="fas fa-save"></i> ${gettext('Lưu')}
                            </button>
                            <button class="cancel-edit-btn btn btn-secondary btn-sm" style="margin-left: 8px;">
                                <i class="fas fa-times"></i> ${gettext('Hủy')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderRatingOptions(currentRating) {
        let options = '';
        for (let i = 1; i <= 5; i++) {
            const selected = i === currentRating ? 'selected' : '';
            options += `<option value="${i}" ${selected}>${i} ${gettext('sao')}</option>`;
        }
        return options;
    }

    renderActionButtons(review) {
        return `
            <div class="review-actions">
                <button class="edit-review-btn btn btn-sm btn-outline-primary" title="${gettext('Sửa đánh giá')}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="delete-review-btn btn btn-sm btn-outline-danger" title="${gettext('Xóa đánh giá')}" style="margin-left: 4px;">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    }

    canUserModifyReview(review) {
        if (!this.currentUser) return false;
        return this.isAdmin || review.user.id === this.currentUser.id;
    }

    editReview(reviewId) {
        const reviewItem = $(`.review-item[data-review-id="${reviewId}"]`);
        reviewItem.find('.review-content-display').hide();
        reviewItem.find('.review-content-edit').show();
        reviewItem.find('.review-actions').hide();
    }

    cancelEdit(reviewId) {
        const reviewItem = $(`.review-item[data-review-id="${reviewId}"]`);
        reviewItem.find('.review-content-display').show();
        reviewItem.find('.review-content-edit').hide();
        reviewItem.find('.review-actions').show();
        
        // Reset form values
        const originalContent = reviewItem.find('.review-content-display').text().trim();
        reviewItem.find('.edit-content-textarea').val(originalContent);
    }

    async saveEdit(reviewId) {
        const reviewItem = $(`.review-item[data-review-id="${reviewId}"]`);
        const newRating = parseInt(reviewItem.find('.edit-rating-select').val());
        const newContent = reviewItem.find('.edit-content-textarea').val().trim();

        if (!newContent) {
            alert(gettext('Nội dung đánh giá không được để trống.'));
            return;
        }

        try {
            const response = await fetch(`/interactions/ajax/${this.novelSlug}/reviews/${reviewId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    rating: newRating,
                    content: newContent
                })
            });

            const data = await response.json();

            if (data.success) {
                // Update the display
                reviewItem.find('.review-content-display').html(this.formatContent(newContent));
                reviewItem.find('.review-rating').html(this.renderStars(newRating));
                
                // Hide edit form
                this.cancelEdit(reviewId);
                
                // Show success message
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || gettext('Có lỗi xảy ra khi cập nhật đánh giá.'), 'error');
            }
        } catch (error) {
            console.error('Error updating review:', error);
            this.showMessage(gettext('Có lỗi xảy ra khi cập nhật đánh giá.'), 'error');
        }
    }

    async deleteReview(reviewId) {
        if (!confirm(gettext('Bạn có chắc chắn muốn xóa đánh giá này?'))) {
            return;
        }

        try {
            const response = await fetch(`/interactions/ajax/${this.novelSlug}/reviews/${reviewId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                // Remove the review item from DOM
                $(`.review-item[data-review-id="${reviewId}"]`).fadeOut(300, function() {
                    $(this).remove();
                });
                
                // Update review count
                const currentCount = parseInt($('.review-count').text().replace(/[()]/g, ''));
                $('.review-count').text(`(${currentCount - 1})`);
                
                // If this was the current user's review, re-enable add review button
                const reviewItem = $(`.review-item[data-review-id="${reviewId}"]`);
                const reviewUserId = reviewItem.data('user-id');
                if (this.currentUser && reviewUserId === this.currentUser.id) {
                    this.userHasReviewed = false;
                    $('#add-review-btn')
                        .prop('disabled', false)
                        .attr('title', gettext('Thêm đánh giá của bạn'));
                }
                
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || gettext('Có lỗi xảy ra khi xóa đánh giá.'), 'error');
            }
        } catch (error) {
            console.error('Error deleting review:', error);
            this.showMessage(gettext('Có lỗi xảy ra khi xóa đánh giá.'), 'error');
        }
    }

    showMessage(message, type = 'info') {
        // Create toast notification
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Add to toast container (create if doesn't exist)
        if (!$('.toast-container').length) {
            $('body').append('<div class="toast-container position-fixed top-0 end-0 p-3"></div>');
        }
        
        const $toast = $(toastHtml);
        $('.toast-container').append($toast);
        
        // Show toast
        const toast = new bootstrap.Toast($toast[0]);
        toast.show();
        
        // Remove after hidden
        $toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }

    getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val() || 
               $('meta[name=csrf-token]').attr('content') ||
               document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
    
    renderStars(rating) {
        let starsHtml = '';
        for (let i = 1; i <= 5; i++) {
            const filled = i <= rating ? 'filled' : '';
            starsHtml += `<i class="fas fa-star ${filled}"></i>`;
        }
        return starsHtml;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = now - date;
        const diffMinutes = Math.floor(diffTime / (1000 * 60));
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMinutes < 1) {
            return gettext('Vừa xong');
        } else if (diffMinutes < 60) {
            return gettext('%s phút trước').replace('%s', diffMinutes);
        } else if (diffHours < 24) {
            return gettext('%s giờ trước').replace('%s', diffHours);
        } else if (diffDays === 1) {
            return gettext('Hôm qua');
        } else if (diffDays < 7) {
            return gettext('%s ngày trước').replace('%s', diffDays);
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return gettext('%s tuần trước').replace('%s', weeks);
        } else {
            return date.toLocaleDateString('vi-VN');
        }
    }
    
    formatContent(content) {
        if (!content) return '';
        
        // Convert line breaks to paragraphs
        const paragraphs = content.split('\n\n').filter(p => p.trim());
        return paragraphs.map(p => `<p>${this.escapeHtml(p.trim())}</p>`).join('');
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
    
    showError() {
        $('#reviews-list').html(`
            <div class="reviews-error" style="text-align: center; padding: 30px; color: #dc3545;">
                <i class="fas fa-exclamation-triangle" style="font-size: 20px; margin-bottom: 8px;"></i>
                <p>${gettext('Không thể tải đánh giá. Vui lòng thử lại sau.')}</p>
            </div>
        `);
    }
}

// Initialize when document is ready
$(document).ready(function() {
    // Get novel slug from the current URL or a data attribute
    const novelSlug = window.location.pathname.split('/')[2]; // Adjust based on your URL structure
    
    if (novelSlug && $('.reviews-section').length > 0) {
        new NovelReviews(novelSlug);
    }
});
