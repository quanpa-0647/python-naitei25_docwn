import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from common.decorators import require_active_novel
from .fake_data import card_list, discussion_data, comments, getNewNovels,top_novels_this_month, new_novels,authors,novels, users,comments,novel_uploads,chapter_uploads,volume_uploads
from django.shortcuts import render
from datetime import date, timedelta
import random
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin,
    )
from django.views.generic.edit import CreateView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from .models import Novel, Tag, NovelTag, Author, Artist, Volume, Chapter, ReadingHistory
from .forms import NovelForm
from constants import (
    MAX_LIMIT_CHUNKS,
    START_POSITION_DEFAULT,
    PROGRESS_DEFAULT,
    DATE_FORMAT_DMY,
    MAX_CHAPTER_LIST,
    MAX_CHAPTER_LIST_PLUS, 
    DATE_FORMAT_DMY, 
    MAX_CHAPTER_LIST,
    ApprovalStatus
)

def Home(request):
    context = {
        "card_list": card_list,
        "discussion_data": discussion_data,
        "comments": comments,
    }
    return render(request, 'novels/home.html', context)
def Admin(request):
    return render(request,'admin/home_admin.html')
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
    return render(request,'admin/users_admin.html',{
        'users' : users
    })
def Novels(request):
    return render(request, 'admin/novels_admin.html', {'novels': novels})

def Requests(request):
    context = {
        "novel_uploads": novel_uploads,
        "volume_uploads": volume_uploads,
        "chapter_uploads": chapter_uploads,
    }
    return render(request,'admin/requests_admin.html',context)
def Comments(request):
    return render(request,'admin/comments_admin.html',{'comments' : comments})

def novel_detail(request, novel_slug):
    novel = get_object_or_404(Novel, slug=novel_slug)
    tags = Tag.objects.filter(noveltag__novel=novel)
    volumes = Volume.objects.filter(novel=novel).prefetch_related("chapters")

    for volume in volumes:
        volume.chapter_list = list(volume.chapters.all())
        volume.remaining_chapters = max(
            len(volume.chapter_list) - MAX_CHAPTER_LIST, 0
        )

    context = {
        'novel': novel,
        'tags': tags,
        'volumes': volumes,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'MAX_CHAPTER_LIST': MAX_CHAPTER_LIST,
        'MAX_CHAPTER_LIST_PLUS': MAX_CHAPTER_LIST_PLUS
    }
    return render(request, "novels/novel_detail.html", context)

@require_active_novel
def chapter_detail_view(request, novel_slug, chapter_slug):
    """Hiển thị chapter với lazy loading"""
    chapter = get_object_or_404(
        Chapter.objects.select_related('volume__novel'),
        slug=chapter_slug,
        volume__novel__slug=novel_slug,
        is_hidden=False, 
        approved=True
    )
    
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
    all_chapters = Chapter.objects.filter(
        volume__novel=chapter.volume.novel,
        approved=True,
        is_hidden=False
    ).select_related('volume').order_by('volume__position', 'position')
    
    context = {
        "chapter": chapter,
        "chunks": initial_chunks,
        "novel": chapter.volume.novel,
        "volume": chapter.volume,
        "next_chapter": next_chapter,
        "prev_chapter": prev_chapter,
        "reading_history": reading_history,
        "all_chapters": all_chapters,
        "total_chunks": chapter.chunks.count(),
        "loaded_chunks": initial_chunks.count(),
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
        if upload_anonymously:
            # If uploading anonymously, set created_by to null
            form.instance.created_by = None
        else:
            # Set created_by to current user
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
