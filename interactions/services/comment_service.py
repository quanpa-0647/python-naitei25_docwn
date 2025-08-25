from django.core.paginator import Paginator
from interactions.models import Comment
from constants import  PAGINATOR_COMMENT_LIST, DEFAULT_PAGE_NUMBER

class CommentService:
    @staticmethod
    def get_novel_comments(novel, page=DEFAULT_PAGE_NUMBER):
        """Lấy comment cha theo phân trang"""
        comments_qs = Comment.objects.filter(
            novel=novel,
            parent_comment__isnull=True,
            is_active=True
        ).select_related("user").prefetch_related("replies__user").order_by("-created_at")

        paginator = Paginator(comments_qs, PAGINATOR_COMMENT_LIST)
        page_obj = paginator.get_page(page)
        return page_obj
