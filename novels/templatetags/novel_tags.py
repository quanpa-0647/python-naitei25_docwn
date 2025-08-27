# novels/templatetags/novel_tags.py
from django import template
from novels.services.novel_filter_service import NovelFilterService
from constants import ProgressStatus, ApprovalStatus

register = template.Library()

@register.inclusion_tag("novels/includes/novel_filter.html", takes_context=True)
def render_novel_filter(context):
    """
    Render novel filter form with search, multi-checkbox tags, sort.
    """
    request = context["request"]
    all_tags = NovelFilterService.get_all_tags_for_filter()
    all_progress_statuses = ProgressStatus.choices
    all_approval_statuses = ApprovalStatus.choices
    selected_tags = request.GET.getlist("tags")
    sort_option = request.GET.get("sort", "created")
    search_query = request.GET.get("q", "")
    author_selected = request.GET.get("author", "")
    artist_selected = request.GET.get("artist", "")
    progress_status_selected = request.GET.get("progress_status", "")
    approval_status_selected = request.GET.get("status", "")

    return {
        "tags": all_tags,
        "progress_statuses": all_progress_statuses,
        "approval_statuses": all_approval_statuses,
        "selected_tags": selected_tags,
        "tag_slugs": selected_tags,  # for compatibility
        "sort_option": sort_option,
        "search_query": search_query,
        "author_selected": author_selected,
        "artist_selected": artist_selected,
        "progress_status_selected": progress_status_selected,
        "approval_status_selected": approval_status_selected,
        # Add status constants for template
        "DRAFT": ApprovalStatus.DRAFT.value,
        "PENDING": ApprovalStatus.PENDING.value,
        "APPROVED": ApprovalStatus.APPROVED.value,
        "REJECTED": ApprovalStatus.REJECTED.value,
    }
