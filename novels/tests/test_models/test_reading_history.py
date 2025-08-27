from django.test import TestCase
from django.contrib.auth import get_user_model
from novels.models import ReadingHistory, Novel, Chapter, Volume, Author, Tag
from constants import ApprovalStatus

User = get_user_model()

class ReadingHistoryModelTestCase(TestCase):
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
    def test_create_reading_history(self):
        rh = ReadingHistory.objects.create(
            user=self.user,
            novel=self.novel,
            chapter=self.chapter,
            reading_progress=0.5
        )
        self.assertEqual(rh.user, self.user)
        self.assertEqual(rh.novel, self.novel)
        self.assertEqual(rh.chapter, self.chapter)
        self.assertEqual(rh.reading_progress, 0.5)
