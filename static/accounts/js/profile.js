document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.querySelector('input[type="file"][name="avatar_upload"]');
    const avatarPreview = document.getElementById('avatarPreview');
    const uploadBtn = document.querySelector('.upload-btn');
    const form = document.querySelector('.profile-form');
    
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 16 * 1024 * 1024) {
                    alert('{% trans "Ảnh quá lớn. Vui lòng chọn ảnh nhỏ hơn 16MB." %}');
                    this.value = '';
                    return;
                }
                
                // Kiểm tra định dạng file
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    alert('{% trans "Định dạng ảnh không được hỗ trợ. Vui lòng chọn file JPG, PNG hoặc GIF." %}');
                    this.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.src = e.target.result;
                    
                    // Thêm visual feedback
                    avatarPreview.style.border = '3px solid #4caf50';
                    setTimeout(() => {
                        avatarPreview.style.border = '3px solid rgba(255,255,255,0.3)';
                    }, 2000);
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const hasFile = avatarInput && avatarInput.files.length > 0;
            
            if (hasFile) {
                form.classList.add('uploading');
                uploadBtn.style.opacity = '0.6';
                
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="icon-upload"></i> {% trans "Đang upload..." %}';
                    submitBtn.disabled = true;
                }
            }
        });
    }
    
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Set initial height
        textarea.style.height = textarea.scrollHeight + 'px';
    });
});
