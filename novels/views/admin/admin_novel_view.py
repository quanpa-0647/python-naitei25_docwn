from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from sympy import Q
from django.core.paginator import Paginator
from novels.models.novel import Novel
from novels.models.tag import Tag
from novels.services import NovelService
from common.decorators import website_admin_required
from constants import (
    DATE_FORMAT_DMYHI,
    PAGINATOR_COMMON_LIST,
    ApprovalStatus,
    PAGINATION_PAGE_RANGE,
    DEFAULT_PAGE_NUMBER,
    ProgressStatus,
    NotificationTypeChoices
)
from interactions.services.notification_service import NotificationService
from common.utils import send_notification_to_user
from asgiref.sync import async_to_sync
from django.utils import timezone

@website_admin_required
def Novels(request):  
    search_query = request.GET.get('q', '')
    progress_status = request.GET.get('progress_status', '')
    approval_status = request.GET.get('approval_status', '')
    tag_id = request.GET.get('tag', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)

    page_obj = NovelService.get_admin_novels_paginated(
        search_query=search_query,
        progress_status=progress_status,
        tag_id=tag_id if tag_id else None,
        approval_status=approval_status,
        page=page,
    )
    
    return render(request, 'admin/pages/novels_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'progress_status': progress_status,
        'approval_status': approval_status,
        'tag_id': tag_id,
        'tags': Tag.objects.all(),
        'progress_choices': ProgressStatus.choices(),
        'approval_choices': ApprovalStatus.choices(),
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

    
@website_admin_required
def upload_novel_requests(request):
    search_query = request.GET.get('q', '')
    progress_status = request.GET.get('progress_status', '')
    approval_status = request.GET.get('approval_status', '')
    tag_id = request.GET.get('tag', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)

    page_obj = NovelService.get_pending_novels_paginated(
        search_query=search_query,
        progress_status=progress_status,
        tag_id=tag_id if tag_id else None,
        approval_status=approval_status,
        page=page,
    )

    return render(request, 'admin/pages/request_novel_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'progress_status': progress_status,
        'approval_status': approval_status,
        'tag_id': tag_id,
        'tags': Tag.objects.all(),
        'progress_choices': ProgressStatus.choices(),
        'approval_choices': ApprovalStatus.choices(),
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })



@website_admin_required
def novel_detail(request, slug):
    """Admin novel detail using service"""
    novel_data = NovelService.get_admin_novel_detail(slug)
    
    if not novel_data:
        return redirect('admin:novels')

    context = {
        'novel': novel_data['novel'],
        'tags': novel_data['tags'],
        'APPROVAL_STATUS': {
            'DRAFT': ApprovalStatus.DRAFT.value,
            'PENDING': ApprovalStatus.PENDING.value,
            'APPROVED': ApprovalStatus.APPROVED.value,
            'REJECTED': ApprovalStatus.REJECTED.value,
        },
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
    }
    return render(request, 'admin/pages/novel_detail.html', context)

@website_admin_required
def novel_request_detail(request, slug):
    """Admin pending novel detail using service"""
    novel_data = NovelService.get_pending_novel_detail(slug)
    
    if not novel_data:
        messages.warning(request, _("Yêu cầu này không còn hiệu lực."))
        return redirect('admin:upload_novel_requests')

    context = {
        'novel': novel_data['novel'],
        'tags': novel_data['tags'],
        'APPROVAL_STATUS': {
            'DRAFT': ApprovalStatus.DRAFT.value,
            'PENDING': ApprovalStatus.PENDING.value,
            'APPROVED': ApprovalStatus.APPROVED.value,
            'REJECTED': ApprovalStatus.REJECTED.value,
        },
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
    }
    return render(request, 'admin/novel_request/novel_request_detail.html', context)

@require_POST
@website_admin_required
def admin_approve_novel(request, slug):
    """Approve novel using service"""
    novel = NovelService.approve_novel(slug)
    if novel:
        notification = NotificationService.create_notification(
            user=novel.created_by,
            title=_("Truyện của bạn đã được duyệt"),
            content=_("Truyện '%(title)s' của bạn đã được duyệt.") % {"title": novel.name},
            notification_type=NotificationTypeChoices.SYSTEM,
            related_object=novel,
        )

        async_to_sync(send_notification_to_user)(
            user_id=novel.created_by.id,
            notification=notification,
            redirect_url=NotificationService.attach_link(notification)
        )

        messages.success(request, _("Tiểu thuyết đã được phê duyệt thành công."))
    else:
        messages.error(request, _("Không thể phê duyệt tiểu thuyết này."))
        
    return redirect('admin:upload_novel_requests')

@require_POST
@website_admin_required
def admin_reject_novel(request, slug):
    """Reject novel using service"""
    reason = request.POST.get('reason')
    novel = NovelService.reject_novel(slug, reason)

    reason_text = _("Lý do: %(reason)s") % {"reason": reason} if reason else ""
    if novel:
        notification = NotificationService.create_notification(
            user=novel.created_by,
            title=_("Truyện của bạn bị từ chối"),
            content=_("Truyện '%(title)s' của bạn đã bị từ chối. '%(reason_text)s'") % {"title": novel.name, "reason_text": reason_text},
            notification_type=NotificationTypeChoices.SYSTEM,
            related_object=novel,
        )

        async_to_sync(send_notification_to_user)(
            user_id=novel.created_by.id,
            notification=notification,
            redirect_url=NotificationService.attach_link(notification)
        )
        messages.success(request, _("Tiểu thuyết đã được từ chối."))
    else:
        messages.error(request, _("Không thể từ chối tiểu thuyết này."))
    
    return redirect('admin:upload_novel_requests')

@require_POST
@website_admin_required
def admin_delete_novel(request, slug):
    """Soft delete novel by setting deleted_at"""
    novel = NovelService.delete_novel(slug)
    if novel:

        # Tạo notification cho tác giả
        notification = NotificationService.create_notification(
            user=novel.created_by,
            title=_("Truyện của bạn đã bị xóa"),
            content=_("Truyện '%(title)s' của bạn đã bị xóa bởi admin.") % {"title": novel.name},
            notification_type=NotificationTypeChoices.SYSTEM,
        )

        async_to_sync(send_notification_to_user)(
            user_id=novel.created_by.id,
            notification=notification
        )

        messages.success(request, _("Tiểu thuyết đã được xóa thành công."))
    else:
        messages.error(request, _("Tiểu thuyết không tồn tại hoặc đã bị xóa."))

    return redirect('admin:admin_novels')
