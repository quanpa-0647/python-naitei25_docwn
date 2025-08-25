from django.core.paginator import Paginator
from django.db.models import Q, Max, Count
from novels.models import ReadingHistory, Novel, Tag
from novels.services.novel_filter_service import NovelFilterService
from constants import (
    NOVEL_PER_PAGE,
    DEFAULT_RATING_AVERAGE,
    SUMMARY_TRUNCATE_WORDS,
    DATE_FORMAT_DMYHI,
)


class ReadingHistoryService:
    """Service for handling reading history operations"""
    
    @staticmethod
    def get_user_reading_history_paginated(
            user, 
            search_query=None, 
            tag_slugs=None, 
            author=None,
            artist=None,
            progress_status=None,
            sort_by="last_read", 
            page=1
        ):
        """
        Get paginated reading history for a user with optional filters.
        Uses NovelFilterService for filtering and sorting.
        """
        # Step 1: Get distinct novels from reading history
        reading_history = (
            ReadingHistory.objects.filter(user=user)
            .values('novel')
            .annotate(
                last_read_at=Max('read_at'),
                chapters_read=Count('chapter', distinct=True)
            )
        )
        novel_ids = [item['novel'] for item in reading_history]

        # Step 2: Get novels queryset
        novels = (
            Novel.objects.filter(id__in=novel_ids, deleted_at__isnull=True)
            .select_related('author', 'artist')
            .prefetch_related('tags')
        )

        # Step 3: Map reading history for extra data
        reading_data_map = {
            item['novel']: {
                'last_read_at': item['last_read_at'],
                'chapters_read': item['chapters_read'],
            }
            for item in reading_history
        }

        # Step 4: Apply filter + sort using NovelFilterService
        novels = NovelFilterService.filter_and_sort(
            novels_queryset=novels,
            search_query=search_query,
            tag_slugs=tag_slugs,
            author=author,
            artist=artist,
            progress_status=progress_status,
            sort_by=sort_by,
            user=user if sort_by == "last_read" else None
        )

        # Step 5: Pagination
        paginator = Paginator(novels, NOVEL_PER_PAGE)
        page_obj = paginator.get_page(page)

        # Step 6: Attach extra data for template
        for novel in page_obj:
            novel.tag_list = list(novel.tags.all())
            novel.author_name = novel.author.name if novel.author else None
            novel.artist_name = novel.artist.name if novel.artist else None
            novel.rating_display = getattr(novel, 'rating_avg', DEFAULT_RATING_AVERAGE) or DEFAULT_RATING_AVERAGE

            # Add reading history specific data
            reading_data = reading_data_map.get(novel.id, {})
            novel.last_read_at = reading_data.get('last_read_at')
            novel.chapters_read = reading_data.get('chapters_read', 0)

        return page_obj
    
    @staticmethod
    def get_reading_history_stats(user):
        """Get reading history statistics for a user"""
        reading_history = ReadingHistory.objects.filter(user=user)
        
        # Total novels read
        total_novels = reading_history.values('novel').distinct().count()
        
        # Total chapters read
        total_chapters = reading_history.count()
        
        # Most read genre
        most_read_genre = (
            reading_history
            .values('novel__tags__name')
            .annotate(count=Count('novel__tags__name'))
            .order_by('-count')
            .first()
        )
        
        return {
            'total_novels': total_novels,
            'total_chapters': total_chapters,
            'most_read_genre': most_read_genre['novel__tags__name'] if most_read_genre else None,
        }
    
    @staticmethod
    def get_latest_reading_chapter(user, novel):
        """Get the latest chapter read by user for a novel"""
        latest_reading = ReadingHistory.objects.filter(
            user=user,
            novel=novel
        ).select_related('chapter').order_by('-read_at').first()
        
        return latest_reading.chapter if latest_reading else None
