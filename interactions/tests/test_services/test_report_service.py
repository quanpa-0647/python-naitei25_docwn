from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from interactions.models import Comment, Report
from novels.models import Novel, Author
from interactions.services.report_service import ReportService
from constants import ApprovalStatus, UserRole

User = get_user_model()

class ReportServiceTests(TestCase):
    def setUp(self):
        # User và Novel + Comment
        self.client = Client()
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )
        author = Author.objects.create(name="Test Author")
        novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            author=author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
        )
        self.comment = Comment.objects.create(user=self.user, novel=novel, content="Test comment")

    def test_create_report_success(self):
        """Tạo report mới thành công"""
        cleaned_data = {"reason": "SPAM", "description": "This is spam"}
        report, error = ReportService.create_report(self.user, self.comment, cleaned_data)

        self.assertIsNotNone(report)
        self.assertIsNone(error)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(report.reason, "SPAM")
        self.assertEqual(report.description, "This is spam")

    def test_prevent_duplicate_report(self):
        """Không cho phép report trùng"""
        cleaned_data = {"reason": "OTHER", "description": "Abusive comment"}
        ReportService.create_report(self.user, self.comment, cleaned_data)

        # Gửi lại
        report, error = ReportService.create_report(self.user, self.comment, cleaned_data)

        self.assertIsNone(report)
        self.assertIsNotNone(error)
        self.assertEqual(Report.objects.count(), 1)  # Chỉ có 1 report duy nhất
