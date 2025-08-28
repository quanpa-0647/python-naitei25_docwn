from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from interactions.models import Comment, Report
from novels.models import Novel, Author
from constants import ApprovalStatus, UserRole

User = get_user_model()

class ReportCommentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )
        # Author
        author = Author.objects.create(name="Test Author")
        # Novel
        novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            author=author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
        )
        self.comment = Comment.objects.create(user=self.user, novel=novel, content="Test comment")
        self.url = reverse("interactions:report_comment", args=[self.comment.id])

    def test_report_comment_success(self):
        """Báo cáo comment thành công"""
        self.client.login(username="user@example.com", password="password123")
        response = self.client.post(self.url, {"reason": "SPAM", "description": "This is spam"})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "Báo cáo đã được gửi.", "report_id": Report.objects.first().id, "comment_id": self.comment.id}
        )
        self.assertEqual(Report.objects.count(), 1)

    def test_report_comment_duplicate(self):
        """Không cho phép báo cáo trùng"""
        self.client.login(username="user@example.com", password="password123")
        self.client.post(self.url, {"reason": "SPAM", "description": "first"})

        response = self.client.post(self.url, {"reason": "SPAM", "description": "duplicate"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bạn đã báo cáo bình luận này rồi.", response.json()["message"])
        self.assertEqual(Report.objects.count(), 1)

    def test_report_comment_unauthenticated(self):
        """User chưa login thì không được báo cáo"""
        response = self.client.post(self.url, {"reason": "SPAM", "description": "not login"})
        # @login_required redirect -> 302
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_report_comment_invalid_form(self):
        """Form không hợp lệ"""
        self.client.login(username="user@example.com", password="password123")
        response = self.client.post(self.url, {"reason": ""})  # thiếu description
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertIn("reason", response.json()["errors"])
