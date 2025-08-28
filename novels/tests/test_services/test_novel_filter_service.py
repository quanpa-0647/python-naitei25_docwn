"""
Unit tests for NovelFilterService functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from novels.services.novel_filter_service import NovelFilterService
from novels.models import Novel, Author, Artist, Tag, ReadingHistory
from constants import ApprovalStatus, ProgressStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class NovelFilterServiceTestCase(TestCase):
    """Test cases for NovelFilterService"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create authors
        self.author1 = Author.objects.create(
            name="John Doe",
            description="Fantasy author"
        )
        self.author2 = Author.objects.create(
            name="Jane Smith", 
            description="Romance author"
        )
        
        # Create artists
        self.artist1 = Artist.objects.create(
            name="Art Master",
            description="Comic artist"
        )
        self.artist2 = Artist.objects.create(
            name="Sketch Artist",
            description="Illustration artist"
        )
        
        # Create tags
        self.tag1 = Tag.objects.create(
            name="Fantasy",
            slug="fantasy",
            description="Fantasy stories"
        )
        self.tag2 = Tag.objects.create(
            name="Romance",
            slug="romance", 
            description="Romance stories"
        )
        self.tag3 = Tag.objects.create(
            name="Adventure",
            slug="adventure",
            description="Adventure stories"
        )
        
        # Create novels
        self.novel1 = Novel.objects.create(
            name="Fantasy Adventure",
            summary="A fantasy adventure story",
            author=self.author1,
            artist=self.artist1,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value,
            view_count=100,
            favorite_count=50,
            rating_avg=4.5
        )
        self.novel1.tags.add(self.tag1, self.tag3)
        
        self.novel2 = Novel.objects.create(
            name="Romance Story",
            summary="A beautiful romance story",
            author=self.author2,
            artist=self.artist2,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.COMPLETED.value,
            view_count=200,
            favorite_count=75,
            rating_avg=4.8
        )
        self.novel2.tags.add(self.tag2)
        
        self.novel3 = Novel.objects.create(
            name="Adventure Quest",
            summary="An epic adventure quest",
            author=self.author1,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value,
            view_count=150,
            favorite_count=60,
            rating_avg=4.2
        )
        self.novel3.tags.add(self.tag3)
        
        # Create volumes and chapters for reading history
        from novels.models import Volume, Chapter
        
        # Volume for novel1
        self.volume1 = Volume.objects.create(
            novel=self.novel1,
            name="Fantasy Volume 1",
            position=1
        )
        self.chapter1 = Chapter.objects.create(
            volume=self.volume1,
            title="The Beginning",
            position=1
        )
        
        # Volume for novel2
        self.volume2 = Volume.objects.create(
            novel=self.novel2,
            name="Sci-Fi Volume 1",
            position=1
        )
        self.chapter2 = Chapter.objects.create(
            volume=self.volume2,
            title="The First Discovery",
            position=1
        )
        
        # Create reading history - Clear any existing reading history first
        ReadingHistory.objects.filter(user=self.user).delete()
        
        import time
        
        # novel2 should be read earlier (3 days ago)  
        ReadingHistory.objects.create(
            user=self.user,
            chapter=self.chapter2,
            novel=self.novel2,
            read_at=timezone.now() - timezone.timedelta(days=3)
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        # novel1 should be read more recently (1 day ago)
        ReadingHistory.objects.create(
            user=self.user,
            chapter=self.chapter1,
            novel=self.novel1,
            read_at=timezone.now() - timezone.timedelta(days=1)
        )


class NovelFilterServiceBasicFilterTests(NovelFilterServiceTestCase):
    """Test basic filtering functionality"""
    
    def test_filter_by_search_query_in_name(self):
        """Test filtering by search query in novel name"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset, 
            search_query="Fantasy"
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertNotIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_search_query_in_author(self):
        """Test filtering by search query in author name"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="Jane"
        )
        
        self.assertNotIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_search_query_in_artist(self):
        """Test filtering by search query in artist name"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="Art Master"
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertNotIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_search_query_in_summary(self):
        """Test filtering by search query in summary"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="beautiful"
        )
        
        self.assertNotIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_search_query_in_tags(self):
        """Test filtering by search query in tag names"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="Romance"
        )
        
        self.assertNotIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)


class NovelFilterServiceTagFilterTests(NovelFilterServiceTestCase):
    """Test tag filtering functionality"""
    
    def test_filter_by_single_tag_slug(self):
        """Test filtering by single tag slug"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            tag_slugs=["fantasy"]
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertNotIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_multiple_tag_slugs(self):
        """Test filtering by multiple tag slugs (OR logic)"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            tag_slugs=["fantasy", "romance"]
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_tag_slug_string(self):
        """Test filtering by single tag slug as string"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            tag_slugs="adventure"
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertNotIn(self.novel2, filtered)
        self.assertIn(self.novel3, filtered)
    
    def test_filter_by_nonexistent_tag(self):
        """Test filtering by non-existent tag slug"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            tag_slugs=["nonexistent"]
        )
        
        self.assertEqual(len(filtered), 0)


class NovelFilterServiceAuthorArtistFilterTests(NovelFilterServiceTestCase):
    """Test author and artist filtering functionality"""
    
    def test_filter_by_author(self):
        """Test filtering by author name"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            author="John"
        )
        
        self.assertIn(self.novel1, filtered)
        self.assertNotIn(self.novel2, filtered)
        self.assertIn(self.novel3, filtered)
    
    def test_filter_by_artist(self):
        """Test filtering by artist name"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            artist="Sketch"
        )
        
        self.assertNotIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)
    
    def test_filter_by_progress_status(self):
        """Test filtering by progress status"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            progress_status=ProgressStatus.COMPLETED.value
        )
        
        self.assertNotIn(self.novel1, filtered)
        self.assertIn(self.novel2, filtered)
        self.assertNotIn(self.novel3, filtered)


class NovelFilterServiceSortingTests(NovelFilterServiceTestCase):
    """Test sorting functionality"""
    
    def test_sort_by_last_read_with_user(self):
        """Test sorting by last read date"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="last_read",
            user=self.user
        )
        
        results = list(filtered)
        # novel1 was read more recently than novel2
        self.assertEqual(results[0], self.novel1)
        self.assertEqual(results[1], self.novel2)
        # novel3 has no reading history so should come last
        self.assertEqual(results[2], self.novel3)
    
    def test_sort_by_last_read_without_user(self):
        """Test sorting by last read without user falls back to default"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="last_read"
        )
        
        # Should fall back to default sorting (created_at desc)
        results = list(filtered)
        self.assertEqual(len(results), 3)
    
    def test_sort_by_created(self):
        """Test sorting by creation date"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="created"
        )
        
        results = list(filtered)
        # Should be ordered by created_at desc (newest first)
        self.assertEqual(results[0], self.novel3)  # Created last
        self.assertEqual(results[1], self.novel2)
        self.assertEqual(results[2], self.novel1)  # Created first
    
    def test_sort_by_updated(self):
        """Test sorting by updated date"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="updated"
        )
        
        results = list(filtered)
        self.assertEqual(len(results), 3)
    
    def test_sort_by_rating(self):
        """Test sorting by rating"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="rating"
        )
        
        results = list(filtered)
        # Should be ordered by rating desc (highest first)
        self.assertEqual(results[0], self.novel2)  # 4.8
        self.assertEqual(results[1], self.novel1)  # 4.5
        self.assertEqual(results[2], self.novel3)  # 4.2
    
    def test_sort_by_name(self):
        """Test sorting by name ascending"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="name"
        )
        
        results = list(filtered)
        # Should be ordered alphabetically
        self.assertEqual(results[0], self.novel3)  # Adventure Quest
        self.assertEqual(results[1], self.novel1)  # Fantasy Adventure
        self.assertEqual(results[2], self.novel2)  # Romance Story
    
    def test_sort_by_name_desc(self):
        """Test sorting by name descending"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="name_desc"
        )
        
        results = list(filtered)
        # Should be ordered reverse alphabetically
        self.assertEqual(results[0], self.novel2)  # Romance Story
        self.assertEqual(results[1], self.novel1)  # Fantasy Adventure
        self.assertEqual(results[2], self.novel3)  # Adventure Quest
    
    def test_sort_by_view_count(self):
        """Test sorting by view count"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="view_count"
        )
        
        results = list(filtered)
        # Should be ordered by view_count desc
        self.assertEqual(results[0], self.novel2)  # 200
        self.assertEqual(results[1], self.novel3)  # 150
        self.assertEqual(results[2], self.novel1)  # 100
    
    def test_sort_by_favorite_count(self):
        """Test sorting by favorite count"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="favorite_count"
        )
        
        results = list(filtered)
        # Should be ordered by favorite_count desc
        self.assertEqual(results[0], self.novel2)  # 75
        self.assertEqual(results[1], self.novel3)  # 60
        self.assertEqual(results[2], self.novel1)  # 50
    
    def test_sort_by_default_unknown(self):
        """Test default sorting for unknown sort option"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            sort_by="unknown_option"
        )
        
        results = list(filtered)
        # Should fall back to default sorting (created_at desc)
        self.assertEqual(len(results), 3)


class NovelFilterServiceCombinedFilterTests(NovelFilterServiceTestCase):
    """Test combined filtering functionality"""
    
    def test_combined_search_and_tag_filter(self):
        """Test combining search query and tag filtering"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="Adventure",
            tag_slugs=["adventure"]
        )
        
        # Should match novels that contain "Adventure" AND have "adventure" tag
        self.assertIn(self.novel1, filtered)  # Fantasy Adventure with adventure tag
        self.assertNotIn(self.novel2, filtered)  # No "Adventure" in name
        self.assertIn(self.novel3, filtered)  # Adventure Quest with adventure tag
    
    def test_combined_author_and_tag_filter(self):
        """Test combining author and tag filtering"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            author="John",
            tag_slugs=["fantasy"]
        )
        
        # Should match novels by John Doe with fantasy tag
        self.assertIn(self.novel1, filtered)  # John Doe + fantasy tag
        self.assertNotIn(self.novel2, filtered)  # Jane Smith
        self.assertNotIn(self.novel3, filtered)  # John Doe but no fantasy tag
    
    def test_combined_all_filters_and_sort(self):
        """Test combining all filters with sorting"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="Adventure",
            tag_slugs=["adventure"],
            author="John",
            sort_by="rating"
        )
        
        results = list(filtered)
        # Should filter by all criteria and sort by rating
        self.assertEqual(len(results), 2)  # novel1 and novel3 match
        # novel1 has higher rating (4.5) than novel3 (4.2)
        self.assertEqual(results[0], self.novel1)
        self.assertEqual(results[1], self.novel3)


class NovelFilterServiceUtilityTests(NovelFilterServiceTestCase):
    """Test utility methods"""
    
    def test_get_all_tags_for_filter(self):
        """Test getting all tags used by novels"""
        tags = NovelFilterService.get_all_tags_for_filter()
        
        # Should return tags that are used by novels
        tag_names = [tag.name for tag in tags]
        self.assertIn("Fantasy", tag_names)
        self.assertIn("Romance", tag_names)
        self.assertIn("Adventure", tag_names)
        
        # Tags should be ordered by name
        self.assertEqual(tags.first().name, "Adventure")
    
    def test_get_all_tags_for_filter_excludes_unused_tags(self):
        """Test that unused tags are excluded"""
        # Create a tag not used by any novel
        unused_tag = Tag.objects.create(
            name="Unused",
            slug="unused",
            description="Unused tag"
        )
        
        tags = NovelFilterService.get_all_tags_for_filter()
        
        # Should not include the unused tag
        tag_names = [tag.name for tag in tags]
        self.assertNotIn("Unused", tag_names)


class NovelFilterServiceEdgeCaseTests(NovelFilterServiceTestCase):
    """Test edge cases and error handling"""
    
    def test_empty_queryset(self):
        """Test filtering on empty queryset"""
        empty_queryset = Novel.objects.none()
        
        filtered = NovelFilterService.filter_and_sort(
            empty_queryset,
            search_query="test"
        )
        
        self.assertEqual(len(filtered), 0)
    
    def test_none_parameters(self):
        """Test filtering with None parameters"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query=None,
            tag_slugs=None,
            author=None,
            artist=None,
            progress_status=None,
            sort_by=None
        )
        
        # Should return all novels with default sorting
        self.assertEqual(len(filtered), 3)
    
    def test_empty_string_parameters(self):
        """Test filtering with empty string parameters"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered = NovelFilterService.filter_and_sort(
            queryset,
            search_query="",
            author="",
            artist=""
        )
        
        # Should return all novels (empty strings are ignored)
        self.assertEqual(len(filtered), 3)
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive"""
        queryset = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        
        filtered_lower = NovelFilterService.filter_and_sort(
            queryset,
            search_query="fantasy"
        )
        
        filtered_upper = NovelFilterService.filter_and_sort(
            queryset,
            search_query="FANTASY"
        )
        
        # Both should return the same results
        self.assertEqual(list(filtered_lower), list(filtered_upper))
        self.assertIn(self.novel1, filtered_lower)
