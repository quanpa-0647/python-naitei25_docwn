from typing import List
from django.contrib.contenttypes.models import ContentType
from interactions.models import Notification
from constants import (
    NotificationTypeChoices
)
from novels.models.chapter import Chapter
from novels.models.novel import Novel
from django.urls import reverse
from common.utils import send_notification_to_user
from asgiref.sync import async_to_sync

class NotificationService:
    @staticmethod
    def get_user_notifications(user, limit: int, offset: int) -> List[Notification]:
        return Notification.objects.filter(user=user).order_by('-created_at')[offset:offset + limit]
    
    @staticmethod
    def create_notification(
        user,
        title: str,
        content: str,
        notification_type: str,
        redirect_url: str = None,
    ) -> Notification:
        """Tạo thông báo mới"""
        notification_data = {
            'user': user,
            'title': title,
            'content': content,
            'type': notification_type,
        }
        
        if redirect_url:
            notification_data.update({
                'redirect_url': redirect_url
            })
            
        notification = Notification.objects.create(**notification_data)
            
        async_to_sync(send_notification_to_user)(
            user_id=user.id,
            notification=notification,
            redirect_url=redirect_url
        )
        
        return notification
