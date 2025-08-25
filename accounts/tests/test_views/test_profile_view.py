from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from unittest.mock import patch

User = get_user_model()


class ProfileViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )
        self.client.login(username="test@example.com", password="123456")

    def test_profile_detail_view_success(self):
        url = reverse("accounts:profile", kwargs={"username": self.user.username})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/profile.html")
        self.assertIn("profile_data", resp.context)

    def test_profile_edit_view_get(self):
        url = reverse("accounts:profile_edit", kwargs={"username": self.user.username})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/profile_edit.html")

    def test_profile_edit_view_post_success(self):
        url = reverse("accounts:profile_edit", kwargs={"username": self.user.username})
        form_data = {"display_name": "Tên mới"}
        resp = self.client.post(url, data=form_data)
        self.assertRedirects(resp, reverse("accounts:profile", kwargs={"username": self.user.username}))
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "Tên mới")

    def test_profile_edit_view_post_fail(self):
        with patch("accounts.forms.ProfileUpdateForm.is_valid", return_value=False):
            url = reverse("accounts:profile_edit", kwargs={"username": self.user.username})
            resp = self.client.post(url, data={"display_name": ""})
            self.assertEqual(resp.status_code, 200)  # render lại form
            self.assertTemplateUsed(resp, "accounts/profile_edit.html")
