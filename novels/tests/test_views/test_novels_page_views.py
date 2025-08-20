from django.test import TestCase
from django.urls import reverse
from novels.models import Novel
from constants import ProgressStatus, ApprovalStatus
from django.utils import timezone
from datetime import timedelta


class NovelViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(20):
            novel = Novel.objects.create(
                name=f"Novel {i}",
                slug=f"novel-{i}",
                summary="Demo summary",
                approval_status=ApprovalStatus.APPROVED.value,
                progress_status=ProgressStatus.ONGOING.value if i % 2 == 0 else ProgressStatus.COMPLETED.value,
                view_count=i,
            )
            novel.created_at = timezone.now() - timedelta(days=i)
            novel.save(update_fields=["created_at"])

    def test_most_read_novels_view(self):
        url = reverse("novels:most_read_novels")
        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "novels/pages/most_read_novels.html")
        self.assertIn("novels", response.context)

        novels = response.context["novels"]
        self.assertTrue(all(novels[i].view_count >= novels[i + 1].view_count for i in range(len(novels) - 1)))

    def test_new_novels_view(self):
        url = reverse("novels:new_novels")
        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "novels/pages/new_novels.html")
        self.assertIn("new_novels", response.context)

        novels = response.context["new_novels"]
        self.assertTrue(all(novels[i].created_at >= novels[i + 1].created_at for i in range(len(novels) - 1)))

    def test_finish_novels_view(self):
        url = reverse("novels:finish_novels")
        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "novels/pages/finish_novels.html")
        self.assertIn("finish_novels", response.context)

        novels = response.context["finish_novels"]
        self.assertTrue(all(n.progress_status == ProgressStatus.COMPLETED.value for n in novels))
