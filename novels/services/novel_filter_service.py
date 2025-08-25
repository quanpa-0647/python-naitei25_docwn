from django.db.models import Q, Max, Count
from novels.models import Novel, Tag, ReadingHistory, Author, Artist

class NovelFilterService:
    """Reusable service for filtering and sorting novels"""

    @staticmethod
    def filter_and_sort(
            novels_queryset, 
            search_query=None, 
            tag_slugs=None, 
            author=None,
            artist=None,
            progress_status=None,
            sort_by="last_read", 
            user=None
    ):
        """
        Filter novels by search, multiple tags, and sort by given option.

        :param novels_queryset: QuerySet of Novel objects
        :param search_query: string to search in novel fields
        :param tag_slugs: list of tag slugs (OR logic)
        :param sort_by: "last_read", "created", "updated", "rating", "name"
        :param user: User object, required if sort_by="last_read"
        :return: sorted list of Novel objects
        """
        # Search filter
        if search_query:
            novels_queryset = novels_queryset.filter(
                Q(name__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(artist__name__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()

        # Tag filter (support multiple tags)
        if tag_slugs:
            if not isinstance(tag_slugs, (list, tuple)):
                tag_slugs = [tag_slugs]
            novels_queryset = novels_queryset.filter(tags__slug__in=tag_slugs).distinct()

        if author:
            novels_queryset = novels_queryset.filter(author__name__icontains=author)

        if artist:
            novels_queryset = novels_queryset.filter(artist__name__icontains=artist)

        # Progress status filter
        if progress_status:
            novels_queryset = novels_queryset.filter(progress_status=progress_status)

        # Sorting
        if sort_by == "last_read" and user:
            # annotate last read date from ReadingHistory
            novels_queryset = novels_queryset.annotate(
                last_read_at=Max('reading_history__read_at', filter=Q(reading_history__user=user))
            ).order_by('-last_read_at')
        elif sort_by == "created":
            novels_queryset = novels_queryset.order_by('-created_at')
        elif sort_by == "updated":
            novels_queryset = novels_queryset.order_by('-updated_at')
        elif sort_by == "rating":
            novels_queryset = novels_queryset.order_by('-rating_avg')
        elif sort_by == "name":
            novels_queryset = novels_queryset.order_by('name')
        elif sort_by == "name_desc":
            novels_queryset = novels_queryset.order_by('-name')
    
        return novels_queryset

    @staticmethod
    def get_all_tags_for_filter():
        """Get all tags that are used by at least one novel"""
        return Tag.objects.filter(novels__isnull=False).distinct().order_by("name")
