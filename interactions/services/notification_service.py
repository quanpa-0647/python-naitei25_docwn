from typing import List
from django.contrib.contenttypes.models import ContentType
from interactions.models import Notification
from constants import (
    NotificationTypeChoices
)

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
        related_object=NotificationTypeChoices,
    ) -> Notification:
        """Tạo thông báo mới"""
        notification_data = {
            'user': user,
            'title': title,
            'content': content,
            'type': notification_type,
        }
        
        if related_object:
            notification_data.update({
                'content_type': ContentType.objects.get_for_model(related_object),
                'object_id': related_object.pk
            })
        
        return Notification.objects.create(**notification_data)
