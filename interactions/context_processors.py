from .services import NotificationService
from .utils import format_notification
from constants import (
    LIMIT_DEFAULT,
    OFFSET_DEFAULT
)

def notifications_context(request):
    if request.user.is_authenticated:
        offset = int(request.GET.get("offset", OFFSET_DEFAULT))
        limit = int(request.GET.get("limit", LIMIT_DEFAULT))
        
        notifications = NotificationService.get_user_notifications(request.user, limit, offset)
        unread_notification_count = request.user.notifications.filter(is_read=False).count()
        return {
            "notifications": [
                format_notification(notification)
                for notification in notifications
            ],
            "unread_notification_count": unread_notification_count
        }
    return {}
