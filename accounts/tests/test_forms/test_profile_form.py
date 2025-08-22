# accounts/forms.py
from django import forms
from django.conf import settings
from accounts.models import UserProfile
from common.utils import ExternalAPIManager
from constants import MIN_TEXTAREA_ROWS, MAX_IMAGE_SIZE


class ProfileUpdateForm(forms.ModelForm):
    avatar_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    class Meta:
        model = UserProfile
        fields = ['display_name', 'gender', 'birthday', 'description', 'interest']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Thêm class cho các field còn lại
        self.fields['display_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})

        # birthday input type date
        self.fields['birthday'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )

        # description + interest: textarea rows
        self.fields['description'].widget.attrs.update({
            'rows': MIN_TEXTAREA_ROWS,
            'class': 'form-control'
        })
        self.fields['interest'].widget.attrs.update({
            'rows': MIN_TEXTAREA_ROWS,
            'class': 'form-control'
        })

        # Avatar upload service check
        if not ExternalAPIManager.is_image_service_available():
            self.fields['avatar_upload'].widget.attrs['disabled'] = True
            self.fields['avatar_upload'].help_text = "Dịch vụ tải ảnh hiện không khả dụng"

    def clean_avatar_upload(self):
        """Validate avatar upload size and content type"""
        avatar = self.cleaned_data.get('avatar_upload')
        if not avatar:
            return avatar

        # Kiểm tra dung lượng
        if avatar.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError("Ảnh vượt quá dung lượng cho phép")

        # Kiểm tra content type
        allowed_types = getattr(settings, "AVATAR_UPLOAD_SETTINGS", {}).get(
            "ALLOWED_CONTENT_TYPES", []
        )
        if allowed_types and avatar.content_type not in allowed_types:
            raise forms.ValidationError("Định dạng ảnh không được hỗ trợ")

        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        avatar = self.cleaned_data.get('avatar_upload')

        if avatar:
            uploaded_url = ExternalAPIManager.upload_image(avatar)
            if not uploaded_url:
                raise Exception("Upload ảnh thất bại")
            profile.avatar = uploaded_url

        if commit:
            profile.save()
        return profile
