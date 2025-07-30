from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import uuid

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from constants import (
    MIN_PASSWORD_LENGTH,
    MIN_SESSION_REMEMBER,
    MAX_SESSION_REMEMBER
)


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, _('Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.'))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, _('Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.'))
        return super().form_invalid(form)


@csrf_protect
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
        return redirect(next_url)
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.can_login():
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(MIN_SESSION_REMEMBER)
                    else:
                        request.session.set_expiry(MAX_SESSION_REMEMBER)
                    
                    messages.success(request, _('Chào mừng %(username)s!') % {'username': user.get_name()})
                    next_url = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
                    return redirect(next_url)
                else:
                    if user.is_blocked:
                        messages.error(request, _('Tài khoản của bạn đã bị khóa.'))
                    else:
                        messages.error(request, _('Tài khoản chưa được kích hoạt.'))
            else:
                messages.error(request, _('Email hoặc mật khẩu không đúng.'))
        else:
            messages.error(request, _('Thông tin đăng nhập không hợp lệ.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.get_name()
        logout(request)
        messages.success(request, _('Tạm biệt %(username)s!') % {'username': username})
    next_url = request.GET.get('next') or settings.LOGOUT_REDIRECT_URL
    return redirect(next_url)


@login_required
def profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Cập nhật thông tin thành công!'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Có lỗi xảy ra. Vui lòng kiểm tra lại.'))
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile,
        'form': form,
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, _('Mật khẩu hiện tại không đúng.'))
        elif new_password != confirm_password:
            messages.error(request, _('Mật khẩu mới không khớp.'))
        elif len(new_password) < MIN_PASSWORD_LENGTH:
            messages.error(request, _('Mật khẩu phải có ít nhất 8 ký tự.'))
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, _('Đổi mật khẩu thành công!'))
            return redirect('accounts:login')
    
    return render(request, 'accounts/change_password.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            reset_token = str(uuid.uuid4())
            user.password_reset_token = reset_token
            user.password_reset_expires = timezone.now() + timedelta(hours=1)
            user.save()

            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{reset_token}/')
            
            messages.success(request, _('Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.'))
            return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, _('Email không tồn tại trong hệ thống.'))
    
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    try:
        user = User.objects.get(
            password_reset_token=token,
            password_reset_expires__gt=timezone.now()
        )
    except User.DoesNotExist:
        messages.error(request, _('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.'))
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, _('Mật khẩu mới không khớp.'))
        elif len(new_password) < MIN_PASSWORD_LENGTH:
            messages.error(request, _('Mật khẩu phải có ít nhất 8 ký tự.'))
        else:
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.save()
            messages.success(request, _('Đặt lại mật khẩu thành công!'))
            return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html', {'token': token})
