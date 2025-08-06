from django.shortcuts import render, redirect, get_object_or_404
from novels.models import Tag, Chapter, Novel, Author, Artist
from django.contrib import messages
from .forms import TagForm, AuthorForm, ArtistForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from constants import (
    PAGINATOR_TAG_LIST, 
    PAGINATOR_COMMON_LIST,
    DEFAULT_PAGE_NUMBER,
    ApprovalStatus,
    DATE_FORMAT_DMYHI
)
from common.decorators import website_admin_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse

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
        return redirect('novels:requests')

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
    return redirect('novels:novel_request')

@require_POST
@website_admin_required
def admin_reject_novel(request, slug):
    novel = get_object_or_404(Novel, slug=slug, approval_status=ApprovalStatus.PENDING.value)
    novel.approval_status = ApprovalStatus.REJECTED.value
    novel.rejected_reason = request.POST.get('reason')
    novel.save()
    return redirect('novels:novel_request')

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

