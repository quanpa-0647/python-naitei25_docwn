from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation

from constants import MIN_PASSWORD_LENGTH


def validate_password(new_password, confirm_password, user=None):
    if new_password != confirm_password:
        return {'valid': False, 'message': _('Mật khẩu mới không khớp.')}

    if not new_password or len(new_password) < MIN_PASSWORD_LENGTH:
        return {'valid': False, 'message': _('Mật khẩu phải có ít nhất %(n)d ký tự.') % {'n': MIN_PASSWORD_LENGTH}}

    try:
        password_validation.validate_password(new_password, user)
    except ValidationError as e:
        return {'valid': False, 'message': ' '.join(e.messages)}

    return {'valid': True, 'message': _('Mật khẩu hợp lệ.')}
