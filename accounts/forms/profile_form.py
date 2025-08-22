# accounts/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.models import UserProfile
from common.utils import ExternalAPIManager
from django.conf import settings
from constants import (
    MIN_TEXTAREA_ROWS,
    MAX_IMAGE_SIZE,
    MAX_IMAGE_SIZE_MB
)


class ProfileUpdateForm(forms.ModelForm):
    avatar_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text=_(f"Chọn ảnh để upload lên ImgBB { settings.AVATAR_UPLOAD_SETTINGS['ALLOWED_CONTENT_TYPES'] }. Tối đa { MAX_IMAGE_SIZE_MB }MB."),
        label=_("Upload ảnh đại diện mới")
    )
    
    class Meta:
        model = UserProfile
        fields = ['display_name', 'gender', 'birthday', 'description', 'interest']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nhập tên hiển thị của bạn')
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': MIN_TEXTAREA_ROWS,
                'placeholder': _('Mô tả về bản thân bạn...')
            }),
            'interest': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': MIN_TEXTAREA_ROWS,
                'placeholder': _('Sở thích, thể loại truyện yêu thích...')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not ExternalAPIManager.is_image_service_available():
            self.fields['avatar_upload'].help_text = _(
                "Dịch vụ upload ảnh hiện không khả dụng. Vui lòng thử lại sau."
            )
            self.fields['avatar_upload'].widget.attrs['disabled'] = True
    
    def clean_avatar_upload(self):
        avatar_upload = self.cleaned_data.get('avatar_upload')
        
        if avatar_upload:
            # Kiểm tra kích thước file (16MB)
            if avatar_upload.size > MAX_IMAGE_SIZE:
                raise forms.ValidationError(_(f'Ảnh quá lớn. Vui lòng chọn ảnh nhỏ hơn { MAX_IMAGE_SIZE_MB }MB.'))
            
            allowed_types = settings.AVATAR_UPLOAD_SETTINGS['ALLOWED_CONTENT_TYPES']
            if avatar_upload.content_type not in allowed_types:
                raise forms.ValidationError(_('Định dạng ảnh không được hỗ trợ.'))
        
        return avatar_upload
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        avatar_upload = self.cleaned_data.get('avatar_upload')
        if avatar_upload:
            try:
                avatar_url = ExternalAPIManager.upload_image(avatar_upload)
                if avatar_url:
                    profile.avatar_url = avatar_url
                else:
                    raise forms.ValidationError(_('Không thể upload ảnh. Vui lòng thử lại.'))
            except Exception as e:
                raise forms.ValidationError(_('Lỗi khi upload ảnh: {}').format(str(e)))
        
        if commit:
            profile.save()
        return profile
