from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from interactions.services import NotificationService
from interactions.models import Notification
from interactions.utils import format_notification
from common.utils import create_sse_response
from constants import (
    LIMIT_DEFAULT,
    OFFSET_DEFAULT,
)

@login_required
def load_more_notifications(request):
    offset = int(request.GET.get("offset", OFFSET_DEFAULT))
    limit = int(request.GET.get("limit", LIMIT_DEFAULT))

    total_count = request.user.notifications.count()
    notifications = NotificationService.get_user_notifications(request.user, limit, offset)

    data = [format_notification(notification) for notification in notifications]

    has_more = total_count > offset + limit

    return JsonResponse({
        "success": True,
        "notifications": data,
        "has_more": has_more
    })


@login_required
@require_http_methods(["POST"])
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    return JsonResponse({"success": True, "id": notification.id})

@login_required
@csrf_exempt
def sse_stream(request):
    user_id = request.user.id
    return create_sse_response(user_id)
