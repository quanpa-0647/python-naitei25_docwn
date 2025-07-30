from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from constants import UserRole
from django.utils.translation import gettext_lazy as _


def user_role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, _('Bạn không có quyền truy cập trang này.'))
                return redirect('accounts:profile')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return user_role_required([UserRole.SYSTEM_ADMIN])(view_func)


def staff_required(view_func):
    return user_role_required([UserRole.WEBSITE_ADMIN, UserRole.SYSTEM_ADMIN])(view_func)


def active_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.can_login():
            messages.error(request, _('Tài khoản của bạn không thể truy cập.'))
            return redirect('accounts:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
