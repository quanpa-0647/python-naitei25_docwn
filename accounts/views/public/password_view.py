from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from accounts.services import PasswordService
from accounts.forms import ChangePasswordForm
from common.utils import send_password_reset_email


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            result = PasswordService.change_password(
                request,
                current_password=form.cleaned_data['current_password'],
                new_password=form.cleaned_data['new_password'],
                confirm_password=form.cleaned_data['confirm_password'],
                keep_session=True,
            )
            if result.get('success'):
                redirect_url = result.get('redirect_url')
                if redirect_url:
                    return redirect(redirect_url)
                return redirect('home')
            else:
                messages.error(request, result.get('message'))
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        result = PasswordService.initiate_password_reset(email)

        if result['success']:
            token = result['reset_token']
            reset_path = reverse('accounts:reset_password', kwargs={'token': token})
            reset_url = request.build_absolute_uri(reset_path)
            
            send_password_reset_email(
                to_email=email,
                subject=_('Đặt lại mật khẩu của bạn'),
                message=_(
                    "Xin chào,\n\n"
                    "Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản của mình.\n"
                    "Vui lòng nhấp vào liên kết sau để đặt lại mật khẩu:\n\n"
                    "%(url)s\n\n"
                    "Nếu bạn không yêu cầu, hãy bỏ qua email này."
                ) % {"url": reset_url}
            )

            messages.success(request, result['message'])
            return redirect('accounts:login')
        else:
            messages.error(request, result['message'])

    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    user = PasswordService.get_user_by_reset_token(token)

    if not user:
        messages.error(request, _('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.'))
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        result = PasswordService.reset_password(user, new_password, confirm_password)
        if result['success']:
            messages.success(request, result['message'])
            return redirect('accounts:login')
        else:
            messages.error(request, result['message'])

    return render(request, 'accounts/reset_password.html', {'token': token})
