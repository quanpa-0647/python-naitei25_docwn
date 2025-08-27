from django.test import TestCase
from django.contrib.auth import get_user_model
from novels.models import Novel, ReadingHistory, Chapter, Volume, Author, Tag
from constants import ApprovalStatus
from novels.services import ReadingHistoryService

User = get_user_model()

class ReadingHistoryServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(name='Test Author')
        self.tag = Tag.objects.create(name='Action', slug='action')
        self.novel = Novel.objects.create(
            name='Test Novel',
            slug='test-novel',
            summary='Test summary',
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        self.novel.tags.add(self.tag)
        self.volume = Volume.objects.create(
            novel=self.novel,
            name='Volume 1',
            position=1
        )
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title='Chapter 1',
            position=1,
            approved=True
        )
        ReadingHistory.objects.create(
            user=self.user,
            novel=self.novel,
            chapter=self.chapter,
            reading_progress=0.5
        )
    def test_pagination(self):
        page_obj = ReadingHistoryService.get_user_reading_history_paginated(
            user=self.user,
            page=1
        )
        self.assertEqual(len(page_obj.object_list), 1)
        self.assertEqual(page_obj.object_list[0].name, 'Test Novel')
    def test_search_filter(self):
        page_obj = ReadingHistoryService.get_user_reading_history_paginated(
            user=self.user,
            search_query='Test Novel',
            page=1
        )
        self.assertEqual(len(page_obj.object_list), 1)
        page_obj = ReadingHistoryService.get_user_reading_history_paginated(
            user=self.user,
            search_query='Nonexistent',
            page=1
        )
        self.assertEqual(len(page_obj.object_list), 0)
    def test_tag_filter(self):
        page_obj = ReadingHistoryService.get_user_reading_history_paginated(
            user=self.user,
            tag_filter='action',
            page=1
        )
        self.assertEqual(len(page_obj.object_list), 1)
        page_obj = ReadingHistoryService.get_user_reading_history_paginated(
            user=self.user,
            tag_filter='nonexistent',
            page=1
        )
        self.assertEqual(len(page_obj.object_list), 0)
    def test_stats(self):
        stats = ReadingHistoryService.get_reading_history_stats(self.user)
        self.assertEqual(stats['total_novels'], 1)
        self.assertEqual(stats['total_chapters'], 1)
        self.assertEqual(stats['most_read_genre'], 'Action')
