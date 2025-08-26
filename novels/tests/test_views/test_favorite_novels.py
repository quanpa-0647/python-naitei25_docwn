from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from novels.models import Novel, Favorite

User = get_user_model()

class NovelViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="password"
        )
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="This is a test novel.",
            created_by=self.user
        )

    def login(self):
        """Helper login đúng USERNAME_FIELD"""
        self.client.login(username="test@example.com", password="password")

    def test_liked_novels_requires_login(self):
        url = reverse("novels:liked_novels")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect login

    def test_liked_novels_empty(self):
        self.login()
        url = reverse("novels:liked_novels")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bạn chưa thích tiểu thuyết nào.")

    def test_liked_novels_with_favorite(self):
        Favorite.objects.create(user=self.user, novel=self.novel)
        self.login()
        url = reverse("novels:liked_novels")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Novel")

    def test_toggle_like_adds_favorite(self):
        self.login()
        url = reverse("novels:toggle_like", args=[self.novel.slug])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"liked": True, "count": 1}
        )
        self.assertTrue(Favorite.objects.filter(user=self.user, novel=self.novel).exists())

    def test_toggle_like_removes_favorite(self):
        self.login()
        url = reverse("novels:toggle_like", args=[self.novel.slug])
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTrue(Favorite.objects.filter(user=self.user, novel=self.novel).exists())
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"liked": False, "count": 0}
        )
        self.assertFalse(Favorite.objects.filter(user=self.user, novel=self.novel).exists())
