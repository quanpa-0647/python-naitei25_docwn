# novels/tests/test_novel_view.py
from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Paginator

from novels.models import Novel
from interactions.models import Comment
from constants import PAGINATOR_COMMENT_LIST
from django.contrib.auth import get_user_model

User = get_user_model()

class NovelCommentsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='12345', email='testuser@example.com'
        )
        self.novel = Novel.objects.create(
            name="Test Novel", slug="test-novel", created_by=self.user
        )
        self.total_comments = 15
        for i in range(self.total_comments):
            Comment.objects.create(
                novel=self.novel,
                user=self.user,
                content=f"Comment {i+1}",
                is_active=True
            )

    def test_novel_comments_returns_json_authenticated(self):
        """Test view trả về JSON đúng khi user đã login"""
        self.client.login(username='testuser', password='12345')
        url = reverse('novels:novel_comments', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url, {'page': 1})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in ["html", "has_next", "has_prev", "page", "num_pages"]:
            self.assertIn(key, data)
        self.assertEqual(data['page'], 1)
        self.assertIsInstance(data['html'], str)

    def test_novel_comments_returns_json_anonymous(self):
        """Test view trả về JSON đúng khi user chưa login"""
        url = reverse('novels:novel_comments', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url, {'page': 1})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("html", data)
        self.assertIsInstance(data['html'], str)

    def test_pagination_logic_matches_paginator(self):
        """Test phân trang JSON khớp với Paginator"""
        paginator = Paginator(
            Comment.objects.filter(
                novel=self.novel, parent_comment__isnull=True, is_active=True
            ).order_by("-created_at"),
            PAGINATOR_COMMENT_LIST
        )
        url = reverse('novels:novel_comments', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url, {'page': 1})
        data = response.json()

        self.assertEqual(data['num_pages'], paginator.num_pages)
        self.assertEqual(data['has_next'], paginator.page(1).has_next())
        self.assertEqual(data['has_prev'], paginator.page(1).has_previous())
