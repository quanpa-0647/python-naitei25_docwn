"""
Unit tests for Admin Novel Views and NotificationService
"""
from http import HTTPStatus
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from novels.models import Novel, Author
from constants import UserRole, ApprovalStatus
from interactions.services.notification_service import NotificationService
from interactions.models import Notification
from unittest.mock import ANY

User = get_user_model()


class AdminNovelViewTests(TestCase):
    """Tests for admin novel approval/rejection views"""

    def setUp(self):
        self.client = Client()
        # Admin user
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role=UserRole.WEBSITE_ADMIN.value,
        )
        # Regular user
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )
        # Author
        self.author = Author.objects.create(name="Test Author")
        # Novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
        )

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    @patch("novels.views.admin.admin_novel_view.NovelService.approve_novel")
    def test_admin_approve_novel_success(self, mock_get_novel, mock_send_notify):
        """Admin approves novel successfully and sends notification"""
        mock_get_novel.return_value = self.novel
        self.client.login(username="admin@example.com", password="password123")

        url = reverse("admin:admin_approve_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_send_notify.assert_called_once_with(
            user_id=self.user.id,
            notification=ANY,
            redirect_url=f"/novels/{self.novel.slug}/",
        )
        

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    @patch("novels.models.Novel.objects.get")
    def test_admin_approve_novel_fail(self, mock_get, mock_send_notify):
        """Admin tries to approve non-existent novel → no notification"""
        mock_get.side_effect = Novel.DoesNotExist

        self.client.login(username="admin@example.com", password="password123")

        url = reverse("admin:admin_approve_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_send_notify.assert_not_called()

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    @patch("novels.views.admin.admin_novel_view.NovelService.reject_novel")
    def test_admin_reject_novel_with_reason(self, mock_get_novel, mock_send_notify):
        """Admin rejects novel with reason"""
        mock_get_novel.return_value = self.novel
        self.client.login(username="admin@example.com", password="password123")

        url = reverse("admin:admin_reject_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url, {"reason": "Không đạt yêu cầu"})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_send_notify.assert_called_once_with(
            user_id=self.user.id,
            notification=ANY,
            redirect_url=f"/novels/{self.novel.slug}/",
        )

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    @patch("novels.views.admin.admin_novel_view.NovelService.reject_novel")
    def test_admin_reject_novel_without_reason(self, mock_get_novel, mock_send_notify):
        """Admin rejects novel without reason"""
        mock_get_novel.return_value = self.novel
        self.client.login(username="admin@example.com", password="password123")

        url = reverse("admin:admin_reject_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_send_notify.assert_called_once_with(
            user_id=self.user.id,
            notification=ANY,
            redirect_url=f"/novels/{self.novel.slug}/",
        )

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    @patch("novels.models.Novel.objects.get")
    def test_admin_reject_novel_fail(self, mock_get_novel, mock_send_notify):
        """Admin tries to reject non-existent novel → no notification"""
        mock_get_novel.side_effect = Novel.DoesNotExist

        self.client.login(username="admin@example.com", password="password123")

        url = reverse("admin:admin_reject_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_send_notify.assert_not_called()
