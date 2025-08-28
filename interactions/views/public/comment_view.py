from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from interactions.models import Comment
from interactions.forms.comment_form import CommentForm

from common.utils import send_notification_to_user
from novels.models import Novel
from interactions.services import CommentService, NotificationService
from django.http import JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from constants import DEFAULT_PAGE_NUMBER, NotificationTypeChoices, UserRole
from django.urls import reverse
from interactions.forms.report_form import ReportForm
from django.core.paginator import Paginator

def novel_comments(request, novel_slug):
    """API trả về HTML comment phân trang"""
    page = request.GET.get("page", DEFAULT_PAGE_NUMBER)
    novel = get_object_or_404(Novel, slug=novel_slug)

    comments_page = CommentService.get_novel_comments(novel, page=page)
    report_form = ReportForm()
    html = render_to_string("novels/includes/comment_list.html", {
        "comments": comments_page,
        "novel_slug": novel_slug,
        "report_form": report_form,
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
            
            redirect_url = reverse("novels:novel_detail", kwargs={"novel_slug": novel.slug}) + f"#comment-container"

            comments_page = CommentService.get_novel_comments(novel, page=DEFAULT_PAGE_NUMBER)
            report_form = ReportForm()
            html = render_to_string("novels/includes/comment_list.html", {
                "comments": comments_page,
                "report_form": report_form,
                "novel_slug": novel_slug
            }, request=request)
            
            NotificationService.create_notification(
                user=novel.created_by,
                title=_("Bình luận mới"),
                content=_(f"Tiểu thuyết { novel.name } của bạn vừa có bình luận mới."),
                notification_type=NotificationTypeChoices.COMMENT,
                redirect_url=redirect_url,
            )
            
            if parent_comment and parent_comment.user != novel.created_by:
                NotificationService.create_notification(
                    user=parent_comment.user,
                    title=_("Phản hồi bình luận"),
                    content=_(f"Bình luận của bạn trên tiểu thuyết { novel.name } vừa có phản hồi."),
                    notification_type=NotificationTypeChoices.COMMENT,
                    redirect_url=redirect_url,
                )

            return JsonResponse({
                "success": True,
                "html": html,
                "has_next": comments_page.has_next(),
                "has_prev": comments_page.has_previous(),
                "page": comments_page.number,
                "num_pages": comments_page.paginator.num_pages,
                "content": comment.content,
                "parent_id": comment.parent_comment.id if comment.parent_comment else None,
            })
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return HttpResponseNotAllowed(['POST'])

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.is_active = False
    comment.save()
    return JsonResponse({"success": True, "id": comment_id})

