from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from novels.services import ReadingHistoryService
from constants import (
    DATE_FORMAT_DMY,
    DATE_FORMAT_DMYHI,
    PAGINATION_PAGE_RANGE,
    SUMMARY_TRUNCATE_WORDS,
    DEFAULT_RATING_AVERAGE,
    DEFAULT_PAGE_NUMBER
)


@login_required
def reading_history_view(request):
    """Reading history page for authenticated users with filter + sort"""

    # --- Query params ---
    search_query = request.GET.get('q', '').strip() or None
    tag_slugs = request.GET.getlist('tags') or None
    sort_option = request.GET.get('sort', 'name')
    author = request.GET.get('author')  
    artist = request.GET.get('artist')  
    progress_status = request.GET.get('progress_status')  

    page = request.GET.get('page', DEFAULT_PAGE_NUMBER)

    # --- Get paginated reading history using new service ---
    page_obj = ReadingHistoryService.get_user_reading_history_paginated(
        user=request.user,
        search_query=search_query,
        tag_slugs=tag_slugs,
        author=author,
        artist=artist,
        progress_status=progress_status,
        sort_by=sort_option,
        page=page
    )

    # --- Reading statistics ---
    stats = ReadingHistoryService.get_reading_history_stats(request.user)

        # --- Attach current_chapter to each novel ---
    novels = page_obj.object_list if page_obj else []
    for novel in novels:
        # giả sử ReadingHistoryService có phương thức trả current_chapter cho 1 novel
        novel.current_chapter = ReadingHistoryService.get_latest_reading_chapter(
            user=request.user,
            novel=novel
        )

    # --- Pagination range ---
    pagination_start = pagination_end = None
    if page_obj:
        current_page = page_obj.number
        pagination_start = current_page - PAGINATION_PAGE_RANGE
        pagination_end = current_page + PAGINATION_PAGE_RANGE

    context = {
        'page_title': _('Lịch sử đọc'),
        'page_obj': page_obj,
        'novels': page_obj.object_list if page_obj else [],
        'search_query': search_query,
        'tag_slugs': tag_slugs,
        'sort_option': sort_option,
        'author_selected': author,
        'artist_selected': artist,
        'progress_status_selected': progress_status,
        'stats': stats,
        'PAGINATION_PAGE_RANGE': PAGINATION_PAGE_RANGE,
        'SUMMARY_TRUNCATE_WORDS': SUMMARY_TRUNCATE_WORDS,
        'DEFAULT_RATING_AVERAGE': DEFAULT_RATING_AVERAGE,
        'pagination_start': pagination_start,
        'pagination_end': pagination_end,
    }

    return render(request, 'novels/pages/reading_history.html', context)
