from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from accounts.forms import ProfileUpdateForm
from accounts.services import ProfileService


@login_required
def profile_view(request):
    user = request.user
    profile = ProfileService.get_user_profile(user)
    
    image_service_status = ProfileService.check_image_service_status()
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        result = ProfileService.update_profile(request, form, profile)
        
        if result['success']:
            return redirect('accounts:profile')
        else:
            context = {
                'user': user,
                'profile': profile,
                'form': form,
                'image_service_status': image_service_status,
                'avatar_info': ProfileService.get_avatar_info(profile),
                'errors': result.get('errors', {})
            }
    else:
        form = ProfileUpdateForm(instance=profile)
        context = {
            'user': user,
            'profile': profile,
            'form': form,
            'image_service_status': image_service_status,
            'avatar_info': ProfileService.get_avatar_info(profile)
        }
    
    return render(request, 'accounts/profile.html', context)
