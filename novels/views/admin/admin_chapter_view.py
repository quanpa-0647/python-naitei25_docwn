from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.urls import reverse
from common.decorators import website_admin_required
from novels.services import ChapterService
from constants import (
    ApprovalStatus,
    DATE_FORMAT_DMYHI,
    PAGINATION_PAGE_RANGE,
    DEFAULT_PAGE_NUMBER,
    DATE_FORMAT_DMY,
)

@website_admin_required
def request_chapter_admin(request):
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    page_obj = ChapterService.get_pending_chapters_for_admin(search_query, page)

    return render(request, 'admin/pages/request_chapter_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@require_POST
@website_admin_required
def approve_chapter_view(request, chapter_slug):
    chapter = ChapterService.get_chapter_by_slug(chapter_slug, for_review=False)
    
    if not chapter:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('admin:request_chapter_admin')
        
    if chapter.approved:
        messages.warning(request, _('Chương này đã được duyệt rồi.'))
        return redirect('admin:chapter_review', chapter_slug=chapter.slug)
    
    ChapterService.approve_chapter(chapter)

    messages.success(request, _('Chương "%(title)s" đã được duyệt thành công!') % {'title': chapter.title})
    return redirect('admin:chapter_review', chapter_slug=chapter.slug)

@require_POST
@website_admin_required
def reject_chapter_view(request, chapter_slug):
    chapter = ChapterService.get_chapter_by_slug(chapter_slug, for_review=False)
    
    if not chapter:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('admin:request_chapter_admin')
        
    if chapter.rejected_reason:
        messages.warning(request, _('Chương này đã bị từ chối rồi.'))
        return redirect('admin:chapter_review', chapter_slug=chapter.slug)
    
    rejected_reason = request.POST.get('rejected_reason', '').strip()

    if not rejected_reason:
        messages.error(request, _('Vui lòng cung cấp lý do từ chối.'))
        return redirect('admin:chapter_review', chapter_slug=chapter.slug)

    ChapterService.reject_chapter(chapter, rejected_reason)

    messages.success(request, _('Chương "%(title)s" đã bị từ chối.') % {'title': chapter.title})
    return redirect('admin:chapter_review', chapter_slug=chapter.slug)

@website_admin_required
def chapter_review(request, chapter_slug):
    chapter = ChapterService.get_chapter_by_slug(chapter_slug, for_review=True)
    
    if not chapter:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('admin:request_chapter_admin')
    
    context = ChapterService.get_chapter_review_context(chapter)
    
    context.update({
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
    })
    
    earliest_unapproved_chapter = ChapterService.get_earliest_unapproved_chapter()
    
    if (earliest_unapproved_chapter and earliest_unapproved_chapter != chapter):
        context['unapproved_chapter_url'] = reverse(
            'admin:chapter_review',
            kwargs={'chapter_slug': earliest_unapproved_chapter.slug}
        )
    else:
        context['unapproved_chapter_url'] = None

    return render(request, 'admin/pages/chapter_review.html', context)
