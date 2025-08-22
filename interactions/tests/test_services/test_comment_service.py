# novels/tests/test_novel_service.py
from django.test import TestCase
from django.core.paginator import Paginator

from novels.models import Novel
from interactions.models import Comment
from novels.services.novel_service import NovelService
from constants import PAGINATOR_COMMENT_LIST

from django.contrib.auth import get_user_model

User = get_user_model()

class NovelServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com', )
        self.novel = Novel.objects.create(name="Test Novel", slug="test-novel", created_by=self.user)
        self.total_comments = 15
        for i in range(self.total_comments):
            Comment.objects.create(
                novel=self.novel,
                user=self.user,
                content=f"Comment {i+1}",
                is_active=True
            )

    def test_get_novel_comments_returns_page_obj(self):
        page_obj = NovelService.get_novel_comments(self.novel, page=1)
        self.assertEqual(page_obj.number, 1)
        self.assertLessEqual(len(page_obj.object_list), PAGINATOR_COMMENT_LIST)
        self.assertEqual(page_obj.paginator.count, self.total_comments)

    def test_get_novel_comments_second_page(self):
        if self.total_comments > PAGINATOR_COMMENT_LIST:
            page2 = NovelService.get_novel_comments(self.novel, page=2)
            self.assertEqual(page2.number, 2)
