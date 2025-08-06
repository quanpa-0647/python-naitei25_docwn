from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from novels.models import Tag, Chapter, Novel, Author, Artist
from django.contrib import messages
from .forms import TagForm, AuthorForm, ArtistForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from .models import Novel
from accounts.models import User
from django.db.models import Prefetch
from django.template.defaultfilters import date as date_filter
from django.utils.timezone import localtime
from constants import (
    PAGINATOR_TAG_LIST, 
    PAGINATOR_COMMON_LIST,
    DEFAULT_PAGE_NUMBER,
    ApprovalStatus,
    DATE_FORMAT_DMYHI,
    UserRole,
    DATE_FORMAT_DMY2
)
from common.decorators import website_admin_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .fake_data import comments, getNewNovels,top_novels_this_month, new_novels,authors,novels,comments,novel_uploads,chapter_uploads,volume_uploads
from django.urls import reverse
@website_admin_required
def Admin(request):
    total_users = User.objects.filter(role = UserRole.USER.value).count()
    total_novels = Novel.objects.count()

    approved_novels = Novel.objects.filter(approval_status=ApprovalStatus.PENDING.value).count()
    unapproved_chapters = Chapter.objects.filter(approved=False).count()
    total_requests = approved_novels + unapproved_chapters
    
    context = {
        'total_users': total_users,
        'total_novels': total_novels,
        'total_requests': total_requests,
        'approved_novels': approved_novels,
        'unapproved_chapters': unapproved_chapters,
    }
    return render(request, 'admin/home_admin.html', context)

@website_admin_required
def Dashboard(request):
    labels, data = getNewNovels()
    return render(request, 'admin/dashboard_admin.html', {
        'labels': labels,
        'data': data,
        'top_novels': top_novels_this_month,
        'new_novels': new_novels,
        'top_authors': authors,
    })

@website_admin_required
def Novels(request):  
    novels = Novel.objects.filter(
    approval_status=ApprovalStatus.APPROVED.value,
    deleted_at__isnull=True
    ).select_related('author').prefetch_related(
    Prefetch(
        'tags',
        queryset=Tag.objects.all(),
        to_attr='tag_list' 
    )).order_by('-created_at')
    result = []
    for novel in novels:
        result.append({
        'name': novel.name,
        'slug': novel.slug,
        'tags': [tag.name for tag in novel.tag_list], 
        'view_count': novel.view_count,
        'author': novel.author.name if novel.author else None,
        'created_at': localtime(novel.created_at).strftime(DATE_FORMAT_DMY2)
    })
    return render(request, 'admin/novels_admin.html', {'novels': novels})

@website_admin_required
def Requests(request):
    context = {
        "novel_uploads": novel_uploads,
        "volume_uploads": volume_uploads,
        "chapter_uploads": chapter_uploads,
    }
    return render(request, 'admin/requests_admin.html', context)

@website_admin_required
def Comments(request):
    return render(request, 'admin/comments_admin.html', {'comments': comments})

@website_admin_required
def upload_novel_requests(request):
    novels = Novel.objects.filter(
        
        approval_status=ApprovalStatus.PENDING.value 
    ).select_related(
        'author',
        'created_by' 
    ).prefetch_related(
        Prefetch(
            'tags',
            queryset=Tag.objects.all(),
            to_attr='tag_list'
        )
    ).order_by('-created_at')

    result = []
    for novel in novels: 
        result.append({
            'name': novel.name,
            'slug': novel.slug,
            'tags': [tag.name for tag in novel.tag_list],
            'created_at': localtime(novel.created_at).strftime(DATE_FORMAT_DMY2),
            'posted_by': novel.created_by.username if novel.created_by else _("Ẩn danh")
        })

    return render(request, 'admin/request_novel_admin.html', {'up_novels': result})

@website_admin_required
def request_chapter_admin(request):
    chapters = Chapter.objects.filter(
        approved=False,
        is_hidden=False
    ).select_related(
        'volume__novel',  
        'volume__novel__created_by'  
    ).order_by('-created_at')

    # Chuẩn bị dữ liệu
    chapter_uploads = []
    for chapter in chapters:
        chapter_uploads.append({
            'novel_name': chapter.volume.novel.name,
            'slug': chapter.slug,
            'chapter_title': chapter.title,
            'submitted_date': localtime(chapter.created_at).strftime(DATE_FORMAT_DMY2),
            'user': chapter.volume.novel.created_by.username if chapter.volume.novel.created_by else "Ẩn danh"
        })

    return render(request, 'admin/request_chapter_admin.html', {
        'chapter_uploads': chapter_uploads,
    })
@website_admin_required
def admin_dashboard(request):
    return redirect('novels:admin_tag_list')

@website_admin_required
def admin_tag_list(request):
    query = request.GET.get("q", "")
    page = request.GET.get("page", DEFAULT_PAGE_NUMBER)

    tags = Tag.objects.all()

    if query:
        tags = tags.filter(
            Q(name__icontains=query) |
            Q(slug__icontains=query) |
            Q(description__icontains=query)
        )

    paginator = Paginator(tags.order_by("slug"), PAGINATOR_TAG_LIST)
    page_obj = paginator.get_page(page)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "admin/tags/partials/list.html", {"tags": page_obj, "query": query})

    return render(request, "admin/tags/tag_list.html", {"tags": page_obj, "query": query})

@website_admin_required
def admin_tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            return JsonResponse({'success': True, 'slug': tag.slug})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})
    return HttpResponseBadRequest(_("Thêm thất bại"))

@website_admin_required
def admin_tag_update(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            tag = form.save()
            return JsonResponse({'success': True, 'slug': tag.slug})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})
    return HttpResponseBadRequest(_("Cập nhật thất bại"))

@website_admin_required
def admin_tag_delete(request, tag_slug):
    if request.method == "POST":
        tag = get_object_or_404(Tag, slug=tag_slug)
        tag.delete()
        return JsonResponse({'success': True})
    return HttpResponseBadRequest(_("Không thể xóa"))

@website_admin_required
def novel_request_detail(request, slug):
    try:
        novel = Novel.objects.get(slug=slug, approval_status=ApprovalStatus.PENDING.value)
    except Novel.DoesNotExist:
        messages.warning(request, _("Yêu cầu này không còn hiệu lực."))
        return redirect('novels:upload_novel_requests')

    tags = Tag.objects.filter(noveltag__novel=novel)

    context = {
        'novel': novel,
        'tags': tags,
        'APPROVAL_STATUS': {
        'DRAFT': ApprovalStatus.DRAFT.value,
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        },
    }
    return render(request, 'admin/novel_request/novel_request_detail.html', context)

@require_POST
@website_admin_required
def admin_approve_novel(request, slug):
    novel = get_object_or_404(Novel, slug=slug, approval_status=ApprovalStatus.PENDING.value)
    novel.approval_status = ApprovalStatus.APPROVED.value
    novel.save()
    return redirect('novels:upload_novel_requests')

@require_POST
@website_admin_required
def admin_reject_novel(request, slug):
    novel = get_object_or_404(Novel, slug=slug, approval_status=ApprovalStatus.PENDING.value)
    novel.approval_status = ApprovalStatus.REJECTED.value
    novel.rejected_reason = request.POST.get('reason')
    novel.save()
    return redirect('novels:upload_novel_requests')

@website_admin_required
def chapter_review(request, chapter_slug):
    chapter = get_object_or_404(Chapter, slug=chapter_slug)
    context = {
        'chapter': chapter,
        'novel': chapter.novel,
        'volume': chapter.volume,
        'content': chapter.get_content(),
        'next_chapter': chapter.get_next_chapter(),
        'previous_chapter': chapter.get_previous_chapter(),
        'chunks': chapter.chunks.all().order_by('position'),
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
    }

    return render(request, 'admin/chapter_review.html', context)
@website_admin_required
def author_list(request):
    search_query = request.GET.get('q', '')
    authors = Author.objects.all().order_by('name')
    if search_query:
        authors = authors.filter(name__icontains=search_query) | authors.filter(pen_name__icontains=search_query)

    paginator = Paginator(authors, PAGINATOR_COMMON_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "title": _("Quản lý Tác giả"),
        "item_name": _("tác giả"),
        "table_partial": "admin/author_artist/partials/list_table_author.html",
        "list_url": reverse('novels:author_list'),
        "create_url": reverse('novels:author_create'),
        "js_path": "admin/js/crud_common.js",
        "page_obj": page_obj,
    }

    return render(request, "admin/author_artist/list_common.html", context)

@website_admin_required
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': AuthorForm()})

@website_admin_required
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': AuthorForm(instance=author)})

@website_admin_required
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    author.delete()
    return JsonResponse({'success': True})

@website_admin_required
def artist_list(request):
    search_query = request.GET.get('q', '')
    artists = Artist.objects.all().order_by('name')
    if search_query:
        artists = artists.filter(name__icontains=search_query) | artists.filter(pen_name__icontains=search_query)

    paginator = Paginator(artists, PAGINATOR_COMMON_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "title": _("Quản lý Họa sĩ"),
        "item_name": _("họa sĩ"),
        "table_partial": "admin/author_artist/partials/list_table_artist.html",
        "list_url": reverse('novels:artist_list'),
        "create_url": reverse('novels:artist_create'),
        "js_path": "admin/js/crud_common.js",
        "page_obj": page_obj,
    }

    return render(request, "admin/author_artist/list_common.html", context)

@website_admin_required
def artist_create(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': ArtistForm()})

@website_admin_required
def artist_update(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': ArtistForm(instance=artist)})

@website_admin_required
def artist_delete(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    artist.delete()
    return JsonResponse({'success': True})

@require_POST
@website_admin_required
def approve_chapter_view(request, chapter_slug):
    chapter = get_object_or_404(Chapter, slug=chapter_slug)
    chapter.approved = True
    chapter.rejected_reason = None
    chapter.save()

    messages.success(request, _('Chương "%(title)s" đã được duyệt thành công!') % {'title': chapter.title})
    return redirect('novels:chapter_review', chapter_slug=chapter.slug)

@require_POST
@website_admin_required
def reject_chapter_view(request, chapter_slug):
    chapter = get_object_or_404(Chapter, slug=chapter_slug)
    rejected_reason = request.POST.get('rejected_reason', '').strip()

    if not rejected_reason:
        messages.error(request, _('Vui lòng cung cấp lý do từ chối.'))
        return redirect('novels:chapter_review', chapter_slug=chapter.slug)

    chapter.approved = False
    chapter.rejected_reason = rejected_reason
    chapter.save()

    messages.success(request, _('Chương "%(title)s" đã bị từ chối.') % {'title': chapter.title})
    return redirect('novels:chapter_review', chapter_slug=chapter.slug)

@website_admin_required
def Users(request):
    users = User.objects.all().values(
        'username',
        'email',
        'date_joined',
        'is_blocked'
    ).order_by('-date_joined')
    user_list = []
    for user in users:
        user_list.append({
            'username': user['username'],
            'email': user['email'],
            'date_joined': localtime(user['date_joined']).strftime(DATE_FORMAT_DMY2),
            'is_blocked': user['is_blocked']
        })

    return render(request, 'admin/users_admin.html', {
        'users': user_list,
    })
def novel_detail(request, slug):
    try:
        novel = Novel.objects.get(slug=slug)
    except Novel.DoesNotExist:
        return redirect('novels:novels')

    tags = Tag.objects.filter(noveltag__novel=novel)

    context = {
        'novel': novel,
        'tags': tags,
        'APPROVAL_STATUS': {
        'DRAFT': ApprovalStatus.DRAFT.value,
        'PENDING': ApprovalStatus.PENDING.value,
        'APPROVED': ApprovalStatus.APPROVED.value,
        'REJECTED': ApprovalStatus.REJECTED.value,
        },
    }
    return render(request, 'admin/novel_detail.html',  context)
