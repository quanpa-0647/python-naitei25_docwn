from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from novels.models import Novel, Tag, Author, Artist
from novels.forms import NovelForm
from constants import ApprovalStatus, ProgressStatus
from http import HTTPStatus

User = get_user_model()


class NovelUpdateViewTests(TestCase):
    """Test cases for novel update functionality"""

    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="password123"
        )
        
        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="password123"
        )
        
        # Create test novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="This is a test novel summary.",
            created_by=self.owner,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name="Fantasy", slug="fantasy")
        self.tag2 = Tag.objects.create(name="Adventure", slug="adventure")
        
        # Create test author and artist
        self.author = Author.objects.create(name="Test Author")
        self.artist = Artist.objects.create(name="Test Artist")

    def test_novel_update_view_get_owner_access(self):
        """Test that novel owner can access update form"""
        self.client.login(username='owner@example.com', password='password123')
        
        url = reverse('novels:novel_update', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Chỉnh sửa tiểu thuyết")
        self.assertIsInstance(response.context['form'], NovelForm)
        self.assertTrue(response.context.get('is_update', False))

    def test_novel_update_view_get_non_owner_access_denied(self):
        """Test that non-owner cannot access update form"""
        self.client.login(username='other@example.com', password='password123')
        
        url = reverse('novels:novel_update', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_novel_update_view_anonymous_user_redirect(self):
        """Test that anonymous user is redirected to login"""
        url = reverse('novels:novel_update', kwargs={'novel_slug': self.novel.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('/accounts/login/', response.url)

    def test_novel_update_post_valid_data(self):
        """Test successful novel update with valid data"""
        self.client.login(username='owner@example.com', password='password123')
        
        url = reverse('novels:novel_update', kwargs={'novel_slug': self.novel.slug})
        
        update_data = {
            'name': 'Updated Novel Name',
            'other_names': 'Alternative Name',
            'summary': 'This is an updated summary that is long enough to pass validation.',
            'progress_status': ProgressStatus.COMPLETED.value,
            'tags': [self.tag1.id, self.tag2.id],
            'author': f'author_{self.author.id}',
            'artist': f'artist_{self.artist.id}',
        }
        
        response = self.client.post(url, update_data)
        
        # Should redirect to novel detail page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('novels:novel_detail', kwargs={'novel_slug': self.novel.slug}))
        
        # Check that novel was updated
        updated_novel = Novel.objects.get(id=self.novel.id)
        self.assertEqual(updated_novel.name, 'Updated Novel Name')
        self.assertEqual(updated_novel.other_names, 'Alternative Name')
        self.assertEqual(updated_novel.progress_status, ProgressStatus.COMPLETED.value)
        self.assertEqual(updated_novel.author, self.author)
        self.assertEqual(updated_novel.artist, self.artist)
        
        # Check tags were updated
        self.assertIn(self.tag1, updated_novel.tags.all())
        self.assertIn(self.tag2, updated_novel.tags.all())

    def test_novel_update_post_invalid_data(self):
        """Test novel update with invalid data"""
        self.client.login(username='owner@example.com', password='password123')
        
        url = reverse('novels:novel_update', kwargs={'novel_slug': self.novel.slug})
        
        invalid_data = {
            'name': '',  # Empty name
            'summary': 'Short',  # Too short summary
            'progress_status': ProgressStatus.ONGOING.value,
        }
        
        response = self.client.post(url, invalid_data)
        
        # Should not redirect and show form with errors
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context['form'].errors)

    def test_novel_update_nonexistent_novel(self):
        """Test update attempt on non-existent novel"""
        self.client.login(username='owner@example.com', password='password123')
        
        url = reverse('novels:novel_update', kwargs={'novel_slug': 'nonexistent-novel'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class NovelUpdateServiceTests(TestCase):
    """Test cases for novel update service methods"""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="password123"
        )
        
        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="password123"
        )
        
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="Test summary.",
            created_by=self.owner,
            approval_status=ApprovalStatus.APPROVED.value
        )

    def test_get_novel_for_update_owner_success(self):
        """Test that owner can get novel for update"""
        from novels.services import NovelService
        
        result = NovelService.get_novel_for_update(
            novel_slug=self.novel.slug,
            user=self.owner
        )
        
        self.assertEqual(result, self.novel)

    def test_get_novel_for_update_non_owner_fails(self):
        """Test that non-owner cannot get novel for update"""
        from novels.services import NovelService
        
        result = NovelService.get_novel_for_update(
            novel_slug=self.novel.slug,
            user=self.other_user
        )
        
        self.assertIsNone(result)

    def test_can_user_update_novel_owner(self):
        """Test permission check for novel owner"""
        from novels.services import NovelService
        
        result = NovelService.can_user_update_novel(self.novel, self.owner)
        self.assertTrue(result)

    def test_can_user_update_novel_non_owner(self):
        """Test permission check for non-owner"""
        from novels.services import NovelService
        
        result = NovelService.can_user_update_novel(self.novel, self.other_user)
        self.assertFalse(result)
