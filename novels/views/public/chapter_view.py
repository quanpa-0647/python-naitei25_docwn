import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from common.utils.sse import send_notification_to_user
from interactions.models.notification import Notification
from accounts.models import User
from novels.models import Novel, Chapter
from novels.models.reading_favorite import Favorite
from novels.models.volume import Volume
from django.urls import reverse
from asgiref.sync import async_to_sync
from novels.services import ChapterService, ReadingService
from novels.forms import ChapterForm
from constants import (
    MAX_LIMIT_CHUNKS, START_POSITION_DEFAULT, PROGRESS_DEFAULT,
    DATE_FORMAT_DMY, ApprovalStatus,
    NotificationTypeChoices,
    UserRole
)
from common.decorators import require_active_novel

@require_active_novel
def chapter_detail_view(request, novel_slug, chapter_slug):
    """Chapter detail view with lazy loading"""
    chapter = ChapterService.get_chapter_for_user(chapter_slug, novel_slug, request.user)
    
    initial_chunks = chapter.chunks.filter(
        position__lte=MAX_LIMIT_CHUNKS
    ).order_by('position')
    
    # Get navigation
    navigation = ChapterService.get_chapter_navigation(chapter)
    
    # Get reading history
    reading_history = ReadingService.get_or_create_reading_history(request.user, chapter)
    
    # Get all chapters for sidebar
    all_chapters = ChapterService.get_all_chapters_for_novel(chapter.volume.novel, request.user)
    
    # Get chunk statistics
    chunk_stats = ChapterService.get_chapter_chunks_stats(chapter)
    
    context = {
        "chapter": chapter,
        "chunks": initial_chunks,
        "novel": chapter.volume.novel,
        "volume": chapter.volume,
        "next_chapter": navigation['next_chapter'],
        "prev_chapter": navigation['prev_chapter'],
        "reading_history": reading_history,
        "all_chapters": all_chapters,
        "total_chunks": chunk_stats['total_chunks'],
        "loaded_chunks": initial_chunks.count(),
        "all_chunks_for_stats": chunk_stats['all_chunks'],
        "avg_chunk_size": chunk_stats['avg_chunk_size'],
        "max_chunk_words": chunk_stats['max_chunk_words'],
        "estimated_reading_time": chunk_stats['estimated_reading_time'],
        "DATE_FORMAT_DMY": DATE_FORMAT_DMY
    }
    return render(request, "novels/pages/chapter_details.html", context)

@require_http_methods(["GET"])
def load_more_chunks(request, chapter_id):
    """AJAX endpoint to load more chunks"""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    start_position = int(request.GET.get('start', START_POSITION_DEFAULT))
    limit = int(request.GET.get('limit', MAX_LIMIT_CHUNKS))
    
    chunks = chapter.chunks.filter(
        position__gte=start_position,
        position__lt=start_position + limit
    ).order_by('position')
    
    chunks_data = []
    for chunk in chunks:
        chunks_data.append({
            'position': chunk.position,
            'content': chunk.content,
            'word_count': chunk.word_count,
        })
    
    has_more = chapter.chunks.filter(
        position__gte=start_position + limit
    ).exists()
    
    return JsonResponse({
        'chunks': chunks_data,
        'has_more': has_more,
        'next_start': start_position + limit
    })

@login_required
@require_http_methods(["POST"])
def save_reading_progress(request):
    """Save reading progress"""
    try:
        data = json.loads(request.body)
        chapter_id = data.get('chapter_id')
        chunk_position = data.get('chunk_position', START_POSITION_DEFAULT)
        reading_progress = data.get('reading_progress', PROGRESS_DEFAULT)
        
        ReadingService.save_reading_progress(
            request.user, chapter_id, chunk_position, reading_progress
        )
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('Đã xảy ra lỗi khi lưu tiến độ đọc: ') + str(e)
        })

@require_active_novel
def chapter_list_view(request, novel_slug):
    """List all chapters of a novel"""
    novel = get_object_or_404(Novel, slug=novel_slug)
    chapters = ChapterService.get_all_chapters_for_novel(novel, request.user)
    
    context = {
        'novel': novel,
        'chapters': chapters,
    }
    return render(request, 'novels/pages/chapter_list.html', context)

@login_required
def chapter_add_view(request, novel_slug):
    """Add new chapter to a novel"""
    novel = get_object_or_404(Novel, slug=novel_slug)
    
    # Check permissions
    if (novel.created_by != request.user or
            novel.approval_status != ApprovalStatus.APPROVED.value):
        messages.error(request, _("Bạn không có quyền thêm chapter cho truyện này."))
        return redirect('novels:novel_detail', novel_slug=novel.slug)
    
    if request.method == 'POST':
        form = ChapterForm(novel=novel, data=request.POST)
        if form.is_valid():
            chapter = form.save()
            
            admins = User.objects.filter(role=UserRole.ADMIN.value)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    type=NotificationTypeChoices.SYSTEM,
                    title=_("Chương mới cần duyệt"),
                    content=_("Truyện '%(novel_name)s' vừa có chương mới '%(chapter_title)s' cần được duyệt.") % {
                        "novel_name": novel.name,
                        "chapter_title": chapter.title
                    },
                    redirect_url=reverse("admin:chapter_review", kwargs={"chapter_slug": chapter.slug}),
                )
            
            messages.success(request, _("Chapter đã được thêm thành công!"))
            return redirect('novels:novel_detail', novel_slug=novel.slug)
    else:
        form = ChapterForm(novel=novel)
    
    context = {
        'novel': novel,
        'form': form,
    }
    return render(request, 'novels/pages/chapter_form.html', context)

@login_required
@require_http_methods(["POST"])
def chapter_delete_view(request, novel_slug, chapter_slug):
    """Soft delete a chapter"""
    chapter = get_object_or_404(
        Chapter.objects.select_related('volume__novel'),
        slug=chapter_slug,
        volume__novel__slug=novel_slug,
        deleted_at__isnull=True
    )
    
    # Check ownership
    if chapter.volume.novel.created_by != request.user:
        messages.error(request, _("Bạn không có quyền xóa chapter này."))
        return redirect('novels:novel_detail', novel_slug=novel_slug)
    
    # Perform soft delete
    chapter.deleted_at = timezone.now()
    chapter.save(update_fields=['deleted_at'])
    
    messages.success(request, _("Chapter đã được xóa thành công."))
    return redirect('novels:novel_detail', novel_slug=novel_slug)

def chapter_upload_rules(request):
    """Static page showing chapter upload rules"""
    return render(request, 'novels/pages/chapter_upload_rules.html')

logger = logging.getLogger(__name__)

def notify_favorites_chapter_approved(chapter):
    try:
        novel = chapter.volume.novel
        favorites_qs = Favorite.objects.filter(novel=novel).select_related("user")
        content_type = ContentType.objects.get_for_model(chapter)
        redirect_url = reverse("novels:novel_detail", kwargs={"novel_slug": novel.slug}) + f"#chapter-{chapter.slug}"

        for fav in favorites_qs:
            user = fav.user
            Notification.objects.create(
                user=user,
                type=NotificationTypeChoices.SYSTEM,
                title=_("Truyện '%(novel_name)s' có chương mới") % {"novel_name": novel.name},
                content=_("Chương '%(chapter_title)s' vừa được duyệt và hiển thị.") % {"chapter_title": chapter.title},
                redirect_url=redirect_url,
            )

    except Exception as e:
        logger.exception("Lỗi khi tạo notification: %s", e)

