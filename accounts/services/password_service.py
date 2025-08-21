from datetime import timedelta
import uuid

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from accounts.models import User
from accounts.utils import validate_password


class PasswordService:
    @staticmethod
    def change_password(request, current_password, new_password, confirm_password, *, keep_session=False):
        user = request.user

        if not user.check_password(current_password):
            return {'success': False, 'message': _('Mật khẩu hiện tại không đúng.')}

        validation_result = validate_password(new_password, confirm_password, user=user)
        if not validation_result['valid']:
            return {'success': False, 'message': validation_result['message']}

        if current_password == new_password:
            return {'success': False, 'message': _('Mật khẩu mới không được trùng mật khẩu hiện tại.')}

        user.set_password(new_password)
        user.save()

        if keep_session:
            update_session_auth_hash(request, user)
            messages.success(request, _('Đổi mật khẩu thành công!'))
            return {'success': True, 'message': _('Đổi mật khẩu thành công!')}
        else:
            messages.success(request, _('Đổi mật khẩu thành công! Vui lòng đăng nhập lại.'))
            return {'success': True, 'message': _('Đổi mật khẩu thành công!'), 'redirect_url': 'accounts:login'}

    @staticmethod
    def initiate_password_reset(email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {'success': False, 'message': _('Email không tồn tại trong hệ thống.')}

        reset_token_plain = str(uuid.uuid4())
        user.password_reset_token = make_password(reset_token_plain)
        user.password_reset_expires = timezone.now() + timedelta(hours=1)
        user.save(update_fields=['password_reset_token', 'password_reset_expires'])

        return {
            'success': True,
            'message': _('Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.'),
            'reset_token': reset_token_plain, 
        }

    @staticmethod
    def get_user_by_reset_token(token):
        if not token:
            return None

        candidates = User.objects.filter(
            Q(password_reset_expires__gt=timezone.now()) &
            Q(password_reset_token__isnull=False)
        ).only('id', 'password_reset_token', 'password_reset_expires', 'email')

        for u in candidates:
            if u.password_reset_token and check_password(token, u.password_reset_token):
                return u
        return None

    @staticmethod
    def reset_password(user, new_password, confirm_password):
        validation_result = validate_password(new_password, confirm_password, user=user)
        if not validation_result['valid']:
            return {'success': False, 'message': validation_result['message']}

        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save(update_fields=['password', 'password_reset_token', 'password_reset_expires'])

        return {'success': True, 'message': _('Đặt lại mật khẩu thành công!')}
