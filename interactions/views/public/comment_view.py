from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from interactions.models import Comment
from interactions.forms.comment_form import CommentForm

from novels.models import Novel
from interactions.services.comment_service import CommentService
from django.http import JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from constants import DEFAULT_PAGE_NUMBER
from django.urls import reverse

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

@login_required
def add_comment(request, novel_slug):
    print("POST data:", request.POST)
    novel = get_object_or_404(Novel, slug=novel_slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        parent_id = request.POST.get('parent_comment_id')
        parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None
        
        if form.is_valid():
            comment = Comment.objects.create(
                novel=novel,
                user=request.user,
                content=form.cleaned_data['content'],
                parent_comment=parent_comment
            )

            if not parent_comment:
                html = render_to_string(
                    "interactions/includes/comment.html",
                    {
                        "comment": comment,
                        "user": request.user,
                        "novel_slug": novel.slug
                    }
                )
            else:  # Nếu là reply, render reply.html
                html = render_to_string(
                    "interactions/includes/reply.html",
                    {
                        "comment": comment,  # đây là reply
                        "user": request.user
                    }
                )

            return JsonResponse({
                "success": True,
                "id": comment.id,
                "content": comment.content,
                "user": comment.user.username,
                "parent_id": parent_id,
                "delete_url": reverse("interactions:delete_comment", args=[comment.id]),
                "html": html
            })
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return HttpResponseNotAllowed(['POST'])

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.is_active = False
    comment.save()
    return JsonResponse({"success": True, "id": comment_id})

