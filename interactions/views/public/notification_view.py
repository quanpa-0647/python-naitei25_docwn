from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from http import HTTPStatus
from django.views.decorators.http import require_http_methods
from interactions.services import NotificationService
from interactions.models import Notification
from interactions.utils import format_notification
from common.utils import create_sse_response, sse_manager
from django.utils import timezone
from asgiref.sync import async_to_sync
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

@require_http_methods(["POST"])
@login_required
def sse_ping(request):
    try:
        user_id = request.user.id
        
        # Kiểm tra xem user có active SSE connections không
        has_connection = False
        if user_id in sse_manager.connections:
            has_connection = len(sse_manager.connections[user_id]) > 0
        
        if has_connection:
            heartbeat_data = {
                'type': 'ping',
                'data': {
                    'status': 'pong',
                    'timestamp': timezone.now().isoformat(),
                    'user_id': user_id
                }
            }
            
            async_to_sync(sse_manager.send_to_user)(user_id, heartbeat_data)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Ping sent',
                'has_connection': True,
                'timestamp': timezone.now().isoformat()
            })
        else:
            return JsonResponse({
                'status': 'success', 
                'message': 'No active connections',
                'has_connection': False,
                'timestamp': timezone.now().isoformat()
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Ping failed',
            'error': str(e)
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
