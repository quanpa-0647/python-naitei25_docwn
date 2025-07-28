from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _
from django.contrib.auth import logout
from django.conf import settings


class UserBlockMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if request.user.is_blocked:
                # Logout user nếu bị block
                logout(request)
                messages.error(request, _('Tài khoản của bạn đã bị khóa.'))
                return redirect('accounts:login')
        return None


class LoginRequiredMiddleware(MiddlewareMixin):
    # Danh sách URL yêu cầu đăng nhập
    REQUIRED_LOGIN_URLS = [
        '/accounts/profile/',
        '/accounts/change-password/',
        '/accounts/logout/',
    ]
    
    # Danh sách URL không yêu cầu đăng nhập
    EXEMPT_URLS = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
    
    def process_request(self, request):
        for exempt_url in self.EXEMPT_URLS:
            if request.path.startswith(exempt_url):
                return None
        
        for required_url in self.REQUIRED_LOGIN_URLS:
            if request.path.startswith(required_url):
                if not request.user.is_authenticated:
                    return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        return None
