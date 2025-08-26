from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from novels.models import Novel, Author
from interactions.models import Notification
from constants import ApprovalStatus, UserRole, NotificationTypeChoices
from unittest.mock import patch

User = get_user_model()

class AdminDeleteNovelViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Tạo admin
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role=UserRole.WEBSITE_ADMIN.value,
        )
        # Tạo user thường (author của novel)
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )
        # Tạo author
        self.author = Author.objects.create(name="Test Author")
        # Tạo novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
        )

    @patch("novels.views.admin.admin_novel_view.send_notification_to_user")
    def test_delete_novel_creates_notification(self, mock_send_notification):
        """Khi admin xóa novel thì phải tạo notification cho created_by"""
        self.client.login(username="admin@example.com", password="password123")
        url = reverse("admin:admin_delete_novel", kwargs={"slug": self.novel.slug})
        response = self.client.post(url)

        # Refresh novel
        self.novel.refresh_from_db()
        self.assertIsNotNone(self.novel.deleted_at)

        # Check có notification được tạo
        notif = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.type, NotificationTypeChoices.SYSTEM)
        self.assertIn(self.novel.name, notif.content)

        mock_send_notification.assert_called_once()
        args, kwargs = mock_send_notification.call_args
        self.assertEqual(kwargs["user_id"], self.user.id)
        self.assertEqual(kwargs["notification"], notif)
        # Check redirect
        self.assertRedirects(response, reverse("admin:admin_novels"))

    def test_delete_novel_not_exist_no_notification(self):
        """Nếu novel không tồn tại thì không tạo notification"""
        self.client.login(username="admin@example.com", password="password123")
        url = reverse("admin:admin_delete_novel", kwargs={"slug": "not-exist"})
        response = self.client.post(url)

        # Không có notification nào
        notif_count = Notification.objects.count()
        self.assertEqual(notif_count, 0)

        # Redirect về danh sách
        self.assertRedirects(response, reverse("admin:admin_novels"))
