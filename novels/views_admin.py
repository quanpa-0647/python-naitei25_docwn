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
    PAGINATION_PAGE_RANGE,
    ApprovalStatus,
    DATE_FORMAT_DMYHI,
    DATE_FORMAT_DMY,
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
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    novels = Novel.objects.filter(
        approval_status=ApprovalStatus.APPROVED.value,
        deleted_at__isnull=True
    ).select_related('author').prefetch_related(
        Prefetch(
            'tags',
            queryset=Tag.objects.all(),
            to_attr='tag_list' 
        )
    ).order_by('-created_at')
    
    # Add search functionality
    if search_query:
        novels = novels.filter(
            Q(name__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Add pagination
    paginator = Paginator(novels, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)
    
    return render(request, 'admin/novels_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

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
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    # For now using fake data, but should be replaced with real Comment model
    # comments_qs = Comment.objects.all().order_by('-created_at')
    
    # Add search and filtering when real model is implemented
    # if search_query:
    #     comments_qs = comments_qs.filter(
    #         Q(content__icontains=search_query) |
    #         Q(user__username__icontains=search_query) |
    #         Q(novel__name__icontains=search_query)
    #     )
    
    # if status_filter:
    #     comments_qs = comments_qs.filter(status=status_filter)
    
    # paginator = Paginator(comments_qs, PAGINATOR_COMMON_LIST)
    # page_obj = paginator.get_page(page)
    
    # Temporary pagination for fake data
    paginator = Paginator(comments, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)
    
    return render(request, 'admin/comments_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@website_admin_required
def upload_novel_requests(request):
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
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

    # Add search functionality
    if search_query:
        novels = novels.filter(
            Q(name__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(created_by__username__icontains=search_query)
        ).distinct()
    
    # Add pagination
    paginator = Paginator(novels, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/request_novel_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@website_admin_required
def request_chapter_admin(request):
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    chapters = Chapter.objects.filter(
        approved=False,
        is_hidden=False,
        rejected_reason__isnull=True
    ).select_related(
        'volume__novel',  
        'volume__novel__created_by'  
    ).order_by('-created_at')
    
    # Add search functionality
    if search_query:
        chapters = chapters.filter(
            Q(title__icontains=search_query) |
            Q(volume__novel__name__icontains=search_query) |
            Q(volume__novel__created_by__username__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(chapters, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/request_chapter_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
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
        return render(request, "admin/tags/partials/list.html", {"tags": page_obj, "query": query, "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE})

    return render(request, "admin/tags/tag_list.html", {"tags": page_obj, "query": query, "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE})

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
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
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
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False,
            is_hidden=False
        ).order_by('-created_at').first()
        
        if not chapter:
            # If no unapproved chapters, get the most recent one
            chapter = Chapter.objects.filter(slug=chapter_slug).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Chương không tồn tại.'))
            return redirect('novels:request_chapter_admin')
    
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
        "search_query": search_query,
        "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
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
        "search_query": search_query,
        "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
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
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False
        ).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Không tìm thấy chương chưa được duyệt với slug này.'))
            return redirect('novels:request_chapter_admin')
    
    chapter.approved = True
    chapter.rejected_reason = None
    chapter.save()

    messages.success(request, _('Chương "%(title)s" đã được duyệt thành công!') % {'title': chapter.title})
    return redirect('novels:chapter_review', chapter_slug=chapter.slug)

@require_POST
@website_admin_required
def reject_chapter_view(request, chapter_slug):
    try:
        # Try to get a single chapter first
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        messages.error(request, _('Chương không tồn tại.'))
        return redirect('novels:request_chapter_admin')
    except Chapter.MultipleObjectsReturned:
        # If multiple chapters have the same slug, get the most recent unapproved one
        chapter = Chapter.objects.filter(
            slug=chapter_slug,
            approved=False
        ).order_by('-created_at').first()
        
        if not chapter:
            messages.error(request, _('Không tìm thấy chương chưa được duyệt với slug này.'))
            return redirect('novels:request_chapter_admin')
    
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
    search_query = request.GET.get('q', '')
    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)
    
    users = User.objects.filter(role=UserRole.USER.value).order_by('-date_joined')
    
    # Add search functionality
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(users, PAGINATOR_COMMON_LIST)
    page_obj = paginator.get_page(page)

    return render(request, 'admin/users_admin.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
    })

@website_admin_required
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
        'DATE_FORMAT_DMYHI': DATE_FORMAT_DMYHI,
    }
    return render(request, 'admin/novel_detail.html',  context)
