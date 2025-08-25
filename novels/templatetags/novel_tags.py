# novels/templatetags/novel_tags.py
from django import template
from novels.services.novel_filter_service import NovelFilterService
from constants import ProgressStatus

register = template.Library()

@register.inclusion_tag("novels/includes/novel_filter.html", takes_context=True)
def render_novel_filter(context):
    """
    Render novel filter form with search, multi-checkbox tags, sort.
    """
    request = context["request"]
    all_tags = NovelFilterService.get_all_tags_for_filter()
    all_progress_statuses = ProgressStatus.choices
    selected_tags = request.GET.getlist("tags")
    sort_option = request.GET.get("sort", "name")
    search_query = request.GET.get("search", "")

    return {
        "tags": all_tags,
        "progress_statuses": all_progress_statuses,
        "selected_tags": selected_tags,
        "sort_option": sort_option,
        "search_query": search_query,
    }
