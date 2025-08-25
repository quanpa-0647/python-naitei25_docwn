# accounts/views/profile_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from accounts.forms import ProfileUpdateForm
from accounts.services import ProfileService
from common.decorators import require_owner_or_admin
from constants import (
    DATE_FORMAT_DMYHI,
    DATE_FORMAT_DMY,
)

User = get_user_model()


def profile_detail_view(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    
    # Kiểm tra quyền xem profile
    if not ProfileService.can_view_profile(request.user, user):
        messages.error(request, _('Bạn không có quyền xem profile này.'))
        return redirect('home')
    
    profile = ProfileService.get_user_profile(user)
    profile_data = ProfileService.get_profile_display_data(user, profile)
    
    if not profile_data:
        messages.error(request, _('Không tìm thấy thông tin profile.'))
        return redirect('home')
    
    formatted_info = ProfileService.format_profile_info(profile_data)
    avatar_info = ProfileService.get_avatar_info(profile)
    
    # Kiểm tra xem user hiện tại có thể chỉnh sửa profile này không
    can_edit = ProfileService.can_edit_profile(request.user, user)
    
    context = {
        'profile_user': user,  # User mà profile thuộc về
        'profile': profile,
        'profile_data': profile_data,
        'formatted_info': formatted_info,
        'avatar_info': avatar_info,
        'can_edit': can_edit,
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
    }
    
    return render(request, 'accounts/profile.html', context)


def get_profile_object(request, username):
    """Helper function để lấy user object cho decorator"""
    return get_object_or_404(User, username=username, is_active=True)


@require_owner_or_admin(get_profile_object)
@login_required
def profile_edit_view(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    profile = ProfileService.get_user_profile(user)
    
    # Kiểm tra service upload ảnh
    image_service_status = ProfileService.check_image_service_status()
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        # Sử dụng service để update profile
        result = ProfileService.update_profile(request, form, profile)
        
        if result['success']:
            return redirect('accounts:profile', username=username)
        else:
            # Errors đã được add vào messages trong service
            pass
    else:
        form = ProfileUpdateForm(instance=profile)
    
    # Lấy thông tin để hiển thị
    profile_data = ProfileService.get_profile_display_data(user, profile)
    avatar_info = ProfileService.get_avatar_info(profile)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'profile_data': profile_data,
        'form': form,
        'image_service_status': image_service_status,
        'avatar_info': avatar_info,
    }
    
    return render(request, 'accounts/profile_edit.html', context)
