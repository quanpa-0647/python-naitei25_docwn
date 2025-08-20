from constants import DATE_FORMAT_DMYHI

def format_notification(notification):
    return {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "is_read": notification.is_read,
        "created_at": notification.created_at
    }
