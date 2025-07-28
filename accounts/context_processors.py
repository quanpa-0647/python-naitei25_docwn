from constants import UserRole

def user_context(request):
    context = {}
    
    if request.user.is_authenticated:
        context.update({
            'user_profile': getattr(request.user, 'profile', None),
            'user_name': request.user.get_name(),
            'user_avatar': getattr(request.user.profile, 'avatar', None) if hasattr(request.user, 'profile') else None,
            'is_admin': request.user.role == UserRole.SYSTEM_ADMIN,
            'is_staff': request.user.role in [UserRole.WEBSITE_ADMIN, UserRole.SYSTEM_ADMIN],
        })
    
    return context
