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
    
    @staticmethod
    def update_profile(request, form, profile):
        try:
            if form.is_valid():
                # Lưu profile với avatar upload
                updated_profile = form.save()
                
                # Thông báo thành công với thông tin cụ thể
                if form.cleaned_data.get('avatar_upload'):
                    messages.success(request, _('Cập nhật thông tin và ảnh đại diện thành công!'))
                else:
                    messages.success(request, _('Cập nhật thông tin thành công!'))
                
                return {
                    'success': True,
                    'message': _('Cập nhật thông tin thành công!'),
                    'profile': updated_profile
                }
            else:
                # Xử lý lỗi form validation
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                error_text = '; '.join(error_messages) if error_messages else _('Có lỗi xảy ra. Vui lòng kiểm tra lại.')
                messages.error(request, error_text)
                
                return {
                    'success': False,
                    'message': error_text,
                    'errors': form.errors
                }
        except Exception as e:
            error_msg = _('Có lỗi xảy ra khi cập nhật: {}').format(str(e))
            messages.error(request, error_msg)
            return {
                'success': False,
                'message': error_msg
            }
