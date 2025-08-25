from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from common.utils import ExternalAPIManager
from django.conf import settings


class ProfileService:
    @staticmethod
    def get_user_profile(user):
        return getattr(user, 'profile', None)
    
    @staticmethod
    def get_avatar_info(profile):
        """Lấy thông tin về avatar của profile"""
        if not profile:
            return {
                'has_avatar': False,
                'avatar_url': settings.DEFAULT_AVATAR_URL,
                'is_external': False
            }
        
        return {
            'has_avatar': bool(profile.avatar_url),
            'avatar_url': profile.get_avatar(),
            'is_external': profile.has_external_avatar()
        }
    
    @staticmethod
    def check_image_service_status():
        """Kiểm tra trạng thái dịch vụ upload ảnh"""
        return {
            'available': ExternalAPIManager.is_image_service_available(),
            'service': 'ImgBB'
        }
    
    @staticmethod
    def get_profile_display_data(user, profile):
        if not profile:
            return None
            
        return {
            'user': user,
            'profile': profile,
            'display_name': profile.get_name(),
            'avatar_url': profile.get_avatar(),
            'is_verified': user.is_email_verified,
            'status': {
                'is_active': user.is_active,
                'is_blocked': user.is_blocked,
                'is_locked': profile.is_locked if profile else False,
            },
            'role_info': {
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_admin': user.is_website_admin(),
                'is_staff': user.is_staff,
            }
        }
    
    @staticmethod
    def format_profile_info(profile_data):
        """Format thông tin profile để hiển thị"""
        if not profile_data:
            return {}
            
        user = profile_data['user']
        profile = profile_data['profile']
        
        formatted_info = {
            'basic_info': [
                {
                    'label': _('Tên đăng nhập'),
                    'value': user.username,
                    'type': 'text'
                },
                {
                    'label': _('Email'),
                    'value': user.email,
                    'type': 'email',
                    'verified': user.is_email_verified
                },
            ],
            'personal_info': [],
            'system_info': [
                {
                    'label': _('Vai trò'),
                    'value': user.get_role_display(),
                    'type': 'role',
                    'role_code': user.role
                },
                {
                    'label': _('Ngày tham gia'),
                    'value': user.date_joined,
                    'type': 'datetime'
                },
                {
                    'label': _('Trạng thái'),
                    'value': _('Hoạt động') if user.is_active and not user.is_blocked else _('Bị khóa'),
                    'type': 'status',
                    'status_code': 'active' if user.is_active and not user.is_blocked else 'blocked'
                }
            ]
        }
        
        if profile:
            if profile.display_name:
                formatted_info['personal_info'].append({
                    'label': _('Tên hiển thị'),
                    'value': profile.display_name,
                    'type': 'text'
                })
            
            if profile.gender:
                formatted_info['personal_info'].append({
                    'label': _('Giới tính'),
                    'value': profile.get_gender_display(),
                    'type': 'text'
                })
            
            if profile.birthday:
                formatted_info['personal_info'].append({
                    'label': _('Ngày sinh'),
                    'value': profile.birthday,
                    'type': 'date'
                })
            
            if profile.description:
                formatted_info['personal_info'].append({
                    'label': _('Mô tả'),
                    'value': profile.description,
                    'type': 'textarea'
                })
            
            if profile.interest:
                formatted_info['personal_info'].append({
                    'label': _('Sở thích'),
                    'value': profile.interest,
                    'type': 'textarea'
                })
        
        return formatted_info
    
    @staticmethod
    def update_profile(request, form, profile):
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Cập nhật profile thành công!'))
                return {'success': True}
            except Exception as e:
                messages.error(request, _('Có lỗi xảy ra khi cập nhật profile: {}').format(str(e)))
                return {'success': False, 'errors': {'form': str(e)}}
        else:
            return {'success': False, 'errors': form.errors}
    
    @staticmethod
    def can_edit_profile(current_user, profile_user):
        if not current_user.is_authenticated:
            return False
        
        if current_user.is_website_admin():
            return True
        
        if current_user == profile_user:
            return True
        
        return False
    
    @staticmethod
    def can_view_profile(current_user, profile_user):
        if hasattr(profile_user, 'profile') and profile_user.profile and profile_user.profile.is_locked:
            if not current_user.is_authenticated:
                return False
            if current_user.is_website_admin() or current_user == profile_user:
                return True
            return False
        
        return profile_user.is_active
