from django.shortcuts import render, redirect, get_object_or_404
from novels.models import Tag
from .forms import TagForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from constants import (
    PAGINATOR_TAG_LIST, 
    DEFAULT_PAGE_NUMBER)
from common.decorators import website_admin_required

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

