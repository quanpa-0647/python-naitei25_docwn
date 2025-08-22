from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from novels.models import Novel
from interactions.services.comment_service import CommentService
from django.http import JsonResponse
from django.template.loader import render_to_string
from constants import DEFAULT_PAGE_NUMBER

def novel_comments(request, novel_slug):
    """API trả về HTML comment phân trang"""
    page = request.GET.get("page", DEFAULT_PAGE_NUMBER)
    novel = get_object_or_404(Novel, slug=novel_slug)

    comments_page = CommentService.get_novel_comments(novel, page=page)

    html = render_to_string("novels/includes/comment_list.html", {
        "comments": comments_page,
        "novel_slug": novel_slug
    }, request=request)

    return JsonResponse({
        "html": html,
        "has_next": comments_page.has_next(),
        "has_prev": comments_page.has_previous(),
        "page": comments_page.number,
        "num_pages": comments_page.paginator.num_pages,
    })
