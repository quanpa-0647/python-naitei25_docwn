import json
import random
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
)
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import CreateView
from django.views.generic import ListView

from common.decorators import require_active_novel
from constants import (
    MAX_LIMIT_CHUNKS,
    START_POSITION_DEFAULT,
    PROGRESS_DEFAULT,
    DATE_FORMAT_DMY,
    DATE_FORMAT_DMYHI,
    MAX_CHAPTER_LIST,
    MAX_CHAPTER_LIST_PLUS,
    MAX_TRUNCATED_REJECTED_REASON_LENGTH,
    NOVEL_PER_PAGE,
    PAGINATION_PAGE_RANGE,
    ApprovalStatus,
    WORDS_PER_MINUTE
)
from .fake_data import (
    card_list, discussion_data, comments, getNewNovels, top_novels_this_month,
    new_novels, authors, novels, users, novel_uploads, chapter_uploads,
    volume_uploads
)
from .forms import NovelForm, ChapterForm
from .models import (
    Novel, Tag, NovelTag, Author, Artist, Volume, Chapter, ReadingHistory
)
from .utils import ChunkManager, SimpleChunker


def Home(request):
    context = {
        "card_list": card_list,
        "discussion_data": discussion_data,
        "comments": comments,
    }
    return render(request, 'novels/home.html', context)


def Admin(request):
    return render(request, 'admin/home_admin.html')


def Dashboard(request):
    labels, data = getNewNovels()
    return render(request, 'admin/dashboard_admin.html', {
        'labels': labels,
        'data': data,
        'top_novels': top_novels_this_month,
        'new_novels': new_novels,
        'top_authors': authors,
    })


def Users(request):
    return render(request, 'admin/users_admin.html', {
        'users': users
    })


def Novels(request):
    return render(request, 'admin/novels_admin.html', {'novels': novels})


def Requests(request):
    context = {
        "novel_uploads": novel_uploads,
        "volume_uploads": volume_uploads,
        "chapter_uploads": chapter_uploads,
    }
    return render(request, 'admin/requests_admin.html', context)


def Comments(request):
    return render(request, 'admin/comments_admin.html', {'comments': comments})


def novel_detail(request, novel_slug):
    novel = get_object_or_404(Novel, slug=novel_slug)
    tags = Tag.objects.filter(noveltag__novel=novel)
    volumes = Volume.objects.filter(novel=novel).prefetch_related("chapters")

    # Check if user is the owner of the novel
    is_owner = request.user.is_authenticated and novel.created_by == request.user

    for volume in volumes:
        if is_owner:
            # Owner can see all chapters (including drafts/unapproved)
            volume.chapter_list = list(volume.chapters.all())
        else:
            # Public view - only approved and visible chapters
            volume.chapter_list = list(volume.chapters.filter(approved=True, is_hidden=False))
        
        volume.remaining_chapters = max(
            len(volume.chapter_list) - MAX_CHAPTER_LIST, 0
        )

    # Check if user can add chapters (is owner and novel is approved)
    can_add_chapter = (
        request.user.is_authenticated and
        novel.created_by == request.user and
        novel.approval_status == ApprovalStatus.APPROVED.value
    )

    context = {
        'novel': novel,
        'tags': tags,
        'volumes': volumes,
        'can_add_chapter': can_add_chapter,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'MAX_CHAPTER_LIST': MAX_CHAPTER_LIST,
        'MAX_CHAPTER_LIST_PLUS': MAX_CHAPTER_LIST_PLUS
    }
    return render(request, "novels/novel_detail.html", context)

@require_active_novel
def chapter_detail_view(request, novel_slug, chapter_slug):
    """Hiển thị chapter với lazy loading"""
    # First try to get the chapter with normal public filters
    try:
        chapter = Chapter.objects.select_related('volume__novel').get(
            slug=chapter_slug,
            volume__novel__slug=novel_slug,
            is_hidden=False,
            approved=True
        )
    except Chapter.DoesNotExist:
        # If not found and user is authenticated, check if they own the chapter
        if request.user.is_authenticated:
            chapter = get_object_or_404(
                Chapter.objects.select_related('volume__novel'),
                slug=chapter_slug,
                volume__novel__slug=novel_slug,
                volume__novel__created_by=request.user
            )
        else:
            # If user is not authenticated, show 404
            raise Http404("No Chapter matches the given query.")
    
    initial_chunks = chapter.chunks.filter(
        position__lte=MAX_LIMIT_CHUNKS
    ).order_by('position')
    
    # Lấy chapter navigation
    next_chapter = chapter.get_next_chapter()
    prev_chapter = chapter.get_previous_chapter()
    
    # Lấy reading history nếu user đã login
    reading_history = None
    if request.user.is_authenticated:
        reading_history, created = ReadingHistory.objects.get_or_create(
            user=request.user,
            chapter=chapter,
            defaults={
                'novel': chapter.volume.novel,
                'reading_progress': PROGRESS_DEFAULT
            }
        )
    
    # Lấy danh sách chapters trong novel để sidebar
    if request.user.is_authenticated and chapter.volume.novel.created_by == request.user:
        # User can see all their own chapters (including drafts/unapproved)
        all_chapters = Chapter.objects.filter(
            volume__novel=chapter.volume.novel
        ).select_related('volume').order_by('volume__position', 'position')
    else:
        # Public view - only approved and visible chapters
        all_chapters = Chapter.objects.filter(
            volume__novel=chapter.volume.novel,
            approved=True,
            is_hidden=False
        ).select_related('volume').order_by('volume__position', 'position')
    
    # Chunking information
    all_chunks = chapter.chunks.all()
    total_chunks = all_chunks.count()
    
    # Calculate chunking statistics
    chunk_word_counts = [chunk.word_count for chunk in all_chunks]
    avg_chunk_size = sum(chunk_word_counts) / len(chunk_word_counts) if chunk_word_counts else 0
    max_chunk_words = max(chunk_word_counts) if chunk_word_counts else 0
    estimated_reading_time = chapter.word_count / WORDS_PER_MINUTE  # Use constant for reading speed
    
    context = {
        "chapter": chapter,
        "chunks": initial_chunks,
        "novel": chapter.volume.novel,
        "volume": chapter.volume,
        "next_chapter": next_chapter,
        "prev_chapter": prev_chapter,
        "reading_history": reading_history,
        "all_chapters": all_chapters,
        "total_chunks": total_chunks,
        "loaded_chunks": initial_chunks.count(),
        # Chunking information
        "all_chunks_for_stats": all_chunks,
        "avg_chunk_size": avg_chunk_size,
        "max_chunk_words": max_chunk_words,
        "estimated_reading_time": estimated_reading_time,
        "DATE_FORMAT_DMY": DATE_FORMAT_DMY
    }
    return render(request, "chapters/chapter_details.html", context)


@require_http_methods(["GET"])
def load_more_chunks(request, chapter_id):
    """AJAX endpoint để load thêm chunks"""
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
    """Lưu tiến độ đọc"""
    try:
        data = json.loads(request.body)
        chapter_id = data.get('chapter_id')
        chunk_position = data.get('chunk_position', START_POSITION_DEFAULT)
        reading_progress = data.get('reading_progress', PROGRESS_DEFAULT)
        
        chapter = get_object_or_404(Chapter, id=chapter_id)
        
        reading_history, created = ReadingHistory.objects.get_or_create(
            user=request.user,
            chapter=chapter,
            defaults={'novel': chapter.volume.novel}
        )
        
        reading_history.reading_progress = reading_progress
        reading_history.current_chunk_position = chunk_position
        reading_history.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('Đã xảy ra lỗi khi lưu tiến độ đọc: ') + str(e)
        })


@require_active_novel
def chapter_list_view(request, novel_slug):
    """Danh sách chapters của novel"""
    novel = get_object_or_404(Novel, slug=novel_slug)
    chapters = Chapter.objects.filter(
        volume__novel=novel,
        approved=True,
        is_hidden=False
    ).select_related('volume').order_by('volume__position', 'position')
    
    context = {
        'novel': novel,
        'chapters': chapters,
    }
    return render(request, 'chapters/chapter_list.html', context)


class NovelCreateView(LoginRequiredMixin, CreateView):
    model = Novel
    form_class = NovelForm
    template_name = "novels/novel_form.html"
    success_url = reverse_lazy("novels:home")
    login_url = reverse_lazy("accounts:login")

    # Lazy text for error messages
    permission_denied_message = _("Bạn cần đăng nhập để tạo tiểu thuyết mới.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tạo tiểu thuyết mới")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        # Check if this is a draft save
        save_as_draft = self.request.POST.get("save_as_draft", False)

        if save_as_draft:
            form.instance.approval_status = ApprovalStatus.DRAFT.value
        else:
            form.instance.approval_status = ApprovalStatus.PENDING.value

        # Handle anonymous upload
        upload_anonymously = form.cleaned_data.get("upload_anonymously", False)
        form.instance.is_anonymous = upload_anonymously

        # Always set created_by to current user for tracking purposes
        form.instance.created_by = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )

        response = super().form_valid(form)

        tags = form.cleaned_data.get("tags")
        if tags:
            for tag in tags:
                NovelTag.objects.create(novel=self.object, tag=tag)

        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class MyNovelsView(LoginRequiredMixin, ListView):
    model = Novel
    template_name = "novels/my_novels.html"
    context_object_name = "novels"
    login_url = reverse_lazy("accounts:login")
    paginate_by = NOVEL_PER_PAGE

    def get_queryset(self):
        """Return novels created by the current user, including all statuses"""
        queryset = Novel.objects.filter(
            created_by=self.request.user,
            deleted_at__isnull=True
        ).select_related('author', 'artist').prefetch_related('tags')
        
        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        valid_statuses = [choice[0] for choice in ApprovalStatus.choices()]
        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(approval_status=status_filter)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tiểu thuyết của tôi")
        context["DATE_FORMAT_DMY"] = DATE_FORMAT_DMY
        context["DATE_FORMAT_DMYHI"] = DATE_FORMAT_DMYHI
        
        # Get counts for each status
        user_novels = Novel.objects.filter(
            created_by=self.request.user,
            deleted_at__isnull=True
        )
        
        context["total_count"] = user_novels.count()
        context["draft_count"] = user_novels.filter(
            approval_status=ApprovalStatus.DRAFT.value
        ).count()
        context["pending_count"] = user_novels.filter(
            approval_status=ApprovalStatus.PENDING.value
        ).count()
        context["approved_count"] = user_novels.filter(
            approval_status=ApprovalStatus.APPROVED.value
        ).count()
        context["rejected_count"] = user_novels.filter(
            approval_status=ApprovalStatus.REJECTED.value
        ).count()
        context["DRAFT"] = ApprovalStatus.DRAFT.value
        context["PENDING"] = ApprovalStatus.PENDING.value
        context["APPROVED"] = ApprovalStatus.APPROVED.value
        context["REJECTED"] = ApprovalStatus.REJECTED.value
        context["MAX_TRUNCATED_REJECTED_REASON_LENGTH"] = (
            MAX_TRUNCATED_REJECTED_REASON_LENGTH
        )
        context["PAGINATION_PAGE_RANGE"] = PAGINATION_PAGE_RANGE
        
        # Calculate pagination range for template
        if 'page_obj' in context and context['page_obj']:
            current_page = context['page_obj'].number
            context["pagination_start"] = current_page - PAGINATION_PAGE_RANGE
            context["pagination_end"] = current_page + PAGINATION_PAGE_RANGE
        
        # Add current filter status for highlighting
        context["current_filter"] = self.request.GET.get('status', 'all')
        
        # Preprocess data to avoid any template queries
        if 'novels' in context:
            for novel in context['novels']:
                # Since we already prefetch_related('tags'), this won't cause additional queries
                novel.tag_list = list(novel.tags.all())
                
                # Preprocess author name based on anonymity setting
                if novel.is_anonymous:
                    novel.author_name = None  # Don't show author for anonymous novels
                else:
                    novel.author_name = novel.author.name if novel.author else None
                
                # Preprocess rating display
                novel.rating_display = novel.rating_avg if novel.rating_avg > 0 else None
                
                # Add business logic flags for template
                novel.can_edit = novel.approval_status in [ApprovalStatus.DRAFT.value, ApprovalStatus.REJECTED.value]
                novel.can_manage_chapters = novel.approval_status == ApprovalStatus.APPROVED.value
                novel.is_rejected_with_reason = (
                    novel.approval_status == ApprovalStatus.REJECTED.value and novel.rejected_reason
                )
        
        return context


@login_required
def chapter_add_view(request, novel_slug):
    """View for adding new chapters to a novel"""
    novel = get_object_or_404(Novel, slug=novel_slug)
    
    # Check if user can add chapters (is owner and novel is approved)
    if (novel.created_by != request.user or
            novel.approval_status != ApprovalStatus.APPROVED.value):
        messages.error(request, _("Bạn không có quyền thêm chapter cho truyện này."))
        return redirect('novels:novel_detail', novel_slug=novel.slug)
    
    if request.method == 'POST':
        form = ChapterForm(novel=novel, data=request.POST)
        if form.is_valid():
            chapter = form.save()
            messages.success(request, _("Chapter đã được thêm thành công!"))
            return redirect('novels:novel_detail', novel_slug=novel.slug)
    else:
        form = ChapterForm(novel=novel)
    
    context = {
        'novel': novel,
        'form': form,
    }
    return render(request, 'chapters/chapter_form.html', context)


def chapter_upload_rules(request):
    """Static page showing chapter upload rules"""
    return render(request, 'chapters/chapter_upload_rules.html')
