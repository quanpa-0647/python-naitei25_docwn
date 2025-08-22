from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from constants import MIN_PASSWORD_LENGTH


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label=_('Mật khẩu hiện tại'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu hiện tại'),
            'autocomplete': 'current-password',
        })
    )
    new_password = forms.CharField(
        label=_('Mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu mới'),
            'autocomplete': 'new-password',
        }),
        min_length=MIN_PASSWORD_LENGTH,
        help_text=_('Mật khẩu phải có ít nhất %(min_length)d ký tự.') % {
            'min_length': MIN_PASSWORD_LENGTH
        }
    )
    confirm_password = forms.CharField(
        label=_('Xác nhận mật khẩu mới'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nhập lại mật khẩu mới'),
            'autocomplete': 'new-password',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_('Mật khẩu hiện tại không đúng.'))
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if not new_password:
            return new_password
        try:
            password_validation.validate_password(new_password, self.user)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError(_('Mật khẩu mới không khớp.'))

        # tránh đặt lại trùng mật khẩu cũ
        current_password = cleaned_data.get('current_password')
        if current_password and new_password and current_password == new_password:
            raise ValidationError(_('Mật khẩu mới không được trùng mật khẩu hiện tại.'))

        return cleaned_data
