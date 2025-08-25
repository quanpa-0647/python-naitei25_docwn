from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from constants import UserRole

def require_login(view_func):
    """Yêu cầu user phải đăng nhập và có thể đăng nhập."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.can_login():
            messages.error(request, _('Tài khoản của bạn đã bị khóa hoặc vô hiệu hóa.'))
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def require_role(*allowed_roles):
    """Decorator kiểm tra role của user."""
    def decorator(view_func):
        @wraps(view_func)
        @require_login
        def wrapper(request, *args, **kwargs):
            if request.user.role not in [role.value for role in allowed_roles]:
                raise PermissionDenied(_("Bạn không có quyền truy cập trang này."))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_group(*group_names):
    """Decorator kiểm tra user có thuộc group nào đó không."""
    def decorator(view_func):
        @wraps(view_func)
        @require_login
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name__in=group_names).exists():
                raise PermissionDenied(_("Bạn không có quyền truy cập trang này."))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_permission(*permission_codenames):
    """Decorator kiểm tra user có permission cụ thể không."""
    def decorator(view_func):
        @wraps(view_func)
        @require_login
        def wrapper(request, *args, **kwargs):
            for perm in permission_codenames:
                if not request.user.has_perm(perm):
                    raise PermissionDenied(_("Bạn không có quyền thực hiện hành động này."))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_owner_or_admin(get_object_func):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            obj = get_object_func(request, *args, **kwargs)
            user = request.user

            if user.role in [UserRole.SYSTEM_ADMIN.value, UserRole.WEBSITE_ADMIN.value]:
                return view_func(request, *args, **kwargs)

            if hasattr(obj, 'email') and obj == user:
                return view_func(request, *args, **kwargs)
            if hasattr(obj, 'created_by') and obj.created_by == user:
                return view_func(request, *args, **kwargs)

            novel = get_related_novel(obj)
            if novel and novel.created_by == user:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied(_("Bạn không có quyền truy cập vào tài nguyên này."))
        return wrapper
    return decorator

def get_related_novel(obj):
    if hasattr(obj, 'novel'):
        return obj.novel
    if hasattr(obj, 'volume') and hasattr(obj.volume, 'novel'):
        return obj.volume.novel
    if hasattr(obj, 'chapter') and hasattr(obj.chapter, 'volume') and hasattr(obj.chapter.volume, 'novel'):
        return obj.chapter.volume.novel
    return None

system_admin_required = require_role(UserRole.SYSTEM_ADMIN)
website_admin_required = require_role(UserRole.SYSTEM_ADMIN, UserRole.WEBSITE_ADMIN)
user_required = require_role(UserRole.SYSTEM_ADMIN, UserRole.WEBSITE_ADMIN, UserRole.USER)

def require_active_novel(view_func):
    @wraps(view_func)
    def wrapper(request, novel_slug, *args, **kwargs):
        from novels.models import Novel
        novel = get_object_or_404(Novel, slug=novel_slug, deleted_at__isnull=True)
        request.novel = novel
        return view_func(request, novel_slug, *args, **kwargs)
    return wrapper
