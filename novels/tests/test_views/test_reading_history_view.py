from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from novels.models import Novel, ReadingHistory, Chapter, Volume, Author, Tag
from constants import ApprovalStatus

User = get_user_model()

class ReadingHistoryViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
    def test_requires_login(self):
        url = reverse('novels:reading_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    def test_authenticated_view(self):
        login_success = self.client.login(email='test@example.com', password='testpass123')
        self.assertTrue(login_success)
        response = self.client.get(reverse('novels:reading_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lịch sử đọc')
        self.assertContains(response, self.novel.name)
        self.assertIn('page_obj', response.context)
        self.assertIn('stats', response.context)
