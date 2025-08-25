from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from django.contrib.auth.models import AnonymousUser
from accounts.services import ProfileService
from unittest.mock import patch

User = get_user_model()


class ProfileServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )
        self.profile = self.user.profile
        self.factory = RequestFactory()

    def test_get_user_profile(self):
        self.assertEqual(ProfileService.get_user_profile(self.user), self.profile)

    def test_get_avatar_info_with_and_without_avatar(self):
        info = ProfileService.get_avatar_info(self.profile)
        self.assertFalse(info["is_external"])
        self.profile.avatar_url = "http://example.com/avatar.jpg"
        info = ProfileService.get_avatar_info(self.profile)
        self.assertTrue(info["is_external"])

    @patch("common.utils.ExternalAPIManager.is_image_service_available", return_value=True)
    def test_check_image_service_status(self, mock_service):
        result = ProfileService.check_image_service_status()
        self.assertTrue(result["available"])
        self.assertEqual(result["service"], "ImgBB")

    def test_get_profile_display_data(self):
        data = ProfileService.get_profile_display_data(self.user, self.profile)
        self.assertIn("display_name", data)
        self.assertEqual(data["user"], self.user)

    def test_format_profile_info(self):
        data = ProfileService.get_profile_display_data(self.user, self.profile)
        formatted = ProfileService.format_profile_info(data)
        self.assertIn("basic_info", formatted)
        self.assertIn("system_info", formatted)

    def test_can_edit_profile(self):
        other_user = User.objects.create_user("other", "o@example.com", "123456")
        self.assertTrue(ProfileService.can_edit_profile(self.user, self.user))
        self.assertFalse(ProfileService.can_edit_profile(other_user, self.user))

    def test_can_view_profile_locked(self):
        self.profile.is_locked = True
        self.profile.save()
        anon = AnonymousUser()
        self.assertFalse(ProfileService.can_view_profile(anon, self.user))
        self.assertTrue(ProfileService.can_view_profile(self.user, self.user))
        with patch.object(User, "is_website_admin", return_value=True):
            admin_user = User.objects.create_user("admin", "a@example.com", "123456")
            self.assertTrue(ProfileService.can_view_profile(admin_user, self.user))
