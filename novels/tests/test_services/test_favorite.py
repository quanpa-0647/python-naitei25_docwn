from django.test import TestCase
from django.contrib.auth import get_user_model
from novels.models.novel import Novel, ApprovalStatus

from novels.models.reading_favorite import Favorite
from novels.services.novel_service import FavoriteService, get_liked_novels

User = get_user_model() 

class FavoriteServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@gmail.com",   
            username="testuser",          
            password="12345"
        )
        self.novel1 = Novel.objects.create(
            name="Novel 1",
            slug="novel-1",
            summary="Test 1",
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
        )
        self.novel2 = Novel.objects.create(
            name="Novel 2",
            slug="novel-2",
            summary="Test 2",
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
        )

    def test_toggle_like_adds_favorite(self):
        result = FavoriteService.toggle_like(self.user, self.novel1)
        self.assertTrue(result)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_toggle_like_removes_favorite(self):
        Favorite.objects.create(user=self.user, novel=self.novel1)
        result = FavoriteService.toggle_like(self.user, self.novel1)
        self.assertFalse(result)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_get_liked_novels(self):
        Favorite.objects.create(user=self.user, novel=self.novel1)
        Favorite.objects.create(user=self.user, novel=self.novel2)

        page = get_liked_novels(self.user, page_number=1, per_page=1)
        self.assertEqual(page.paginator.count, 2)
        self.assertEqual(len(page.object_list), 1)
