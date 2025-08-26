from django.test import TestCase
from django.utils import timezone
from novels.models import Novel
from novels.services.novel_service import NovelService
from constants import ApprovalStatus

class NovelServiceDeleteTests(TestCase):
    def setUp(self):
        self.novel = Novel.objects.create(
            name="Test novel",
            slug="test-novel",
            approval_status=ApprovalStatus.APPROVED.value
        )

    def test_delete_novel_success(self):
        novel = NovelService.delete_novel(self.novel.slug)
        self.assertIsNotNone(novel.deleted_at)

    def test_delete_novel_not_found(self):
        result = NovelService.delete_novel("not-exist")
        self.assertFalse(result)
