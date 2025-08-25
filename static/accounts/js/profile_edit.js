document.addEventListener('DOMContentLoaded', function() {
    // Preview uploaded avatar
    const avatarInput = document.querySelector('input[type="file"][name="avatar_upload"]');
    const currentAvatar = document.getElementById('current-avatar');
    const avatarOverlay = document.querySelector('.avatar-overlay');

    const maxFileSizeMB = 16; // 16MB
    const maxFileSizeBytes = maxFileSizeMB * 1024 * 1024
    
    if (avatarInput && currentAvatar) {
        // Click overlay to trigger file input
        if (avatarOverlay) {
            avatarOverlay.addEventListener('click', function() {
                avatarInput.click();
            });
        }
        
        // Preview selected image
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    alert(gettext('Định dạng ảnh không được hỗ trợ.'));
                    this.value = '';
                    return;
                }
                
                // Validate file size (16MB)
                const maxSize = maxFileSizeBytes; // 16MB in bytes
                if (file.size > maxSize) {
                    alert(gettext(`File quá lớn. Vui lòng chọn file nhỏ hơn ${ maxFileSizeMB }MB`));
                    this.value = '';
                    return;
                }
                
                // Preview image
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentAvatar.src = e.target.result;
                    // Add a subtle animation
                    currentAvatar.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        currentAvatar.style.transform = 'scale(1)';
                    }, 150);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form validation
    const form = document.getElementById('profile-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const errors = [];

            // Validate display name
            const displayName = form.querySelector('[name="display_name"]');
            if (displayName && displayName.value.trim().length > 100) {
                errors.push(gettext('Tên hiển thị không được vượt quá 100 ký tự'));
                isValid = false;
            }

            // Validate birthday
            const birthday = form.querySelector('[name="birthday"]');
            if (birthday && birthday.value) {
                const birthDate = new Date(birthday.value);
                const today = new Date();
                const age = today.getFullYear() - birthDate.getFullYear();
                
                if (birthDate > today) {
                    errors.push(gettext('Ngày sinh không thể là tương lai'));
                    isValid = false;
                } else if (age > 120) {
                    errors.push(gettext('Ngày sinh không hợp lệ'));
                    isValid = false;
                }
            }

            // Validate description length
            const description = form.querySelector('[name="description"]');
            if (description && description.value.length > 1000) {
                errors.push(gettext('Mô tả không được vượt quá 1000 ký tự'));
                isValid = false;
            }

            // Validate interest length
            const interest = form.querySelector('[name="interest"]');
            if (interest && interest.value.length > 1000) {
                errors.push(gettext('Sở thích không được vượt quá 1000 ký tự'));
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
                alert('Lỗi:\n' + errors.join('\n'));
                return false;
            }

            // Show loading state
            const submitBtn = form.querySelector('.btn-save');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
                submitBtn.disabled = true;
            }
        });
    }

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Initial resize
        autoResize(textarea);
        
        // Resize on input
        textarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Character counter
        addCharacterCounter(textarea);
    });

    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }

    function addCharacterCounter(textarea) {
        const maxLength = textarea.name === 'description' || textarea.name === 'interest' ? 1000 : 500;
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted character-counter';
        counter.style.textAlign = 'right';
        counter.style.display = 'block';
        
        const updateCounter = () => {
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength}/${maxLength} ký tự`;
            
            if (currentLength > maxLength * 0.9) {
                counter.style.color = '#dc3545';
            } else if (currentLength > maxLength * 0.7) {
                counter.style.color = '#ffc107';
            } else {
                counter.style.color = '#6c757d';
            }
        };

        textarea.addEventListener('input', updateCounter);
        textarea.parentNode.appendChild(counter);
        updateCounter();
    }

    // Smooth form section navigation
    const sectionTitles = document.querySelectorAll('.form-section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function() {
            this.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });

    // Add fade-in animation
    const formSections = document.querySelectorAll('.avatar-section, .basic-info-section, .detail-info-section');
    formSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 200);
    });

    // Confirm navigation away with unsaved changes
    let formChanged = false;
    const formInputs = form.querySelectorAll('input, textarea, select');
    
    formInputs.forEach(input => {
        input.addEventListener('change', () => {
            formChanged = true;
        });
    });

    // Warning before leaving page
    window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
            const confirmationMessage = gettext('Bạn có thay đổi chưa được lưu. Bạn có chắc muốn rời khỏi trang này?');
            e.returnValue = confirmationMessage;
            return confirmationMessage;
        }
    });

    // Remove warning when form is submitted
    if (form) {
        form.addEventListener('submit', function() {
            formChanged = false;
        });
    }

    // Reset form changed flag when form is reset
    const resetButtons = document.querySelectorAll('[type="reset"], .btn-secondary');
    resetButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.classList.contains('btn-secondary')) {
                if (formChanged && !confirm(gettext('Bạn có thay đổi chưa được lưu. Bạn có chắc muốn hủy?'))) {
                    return false;
                }
            }
            formChanged = false;
        });
    });
});
