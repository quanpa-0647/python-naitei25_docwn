from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch, Mock

from accounts.pipeline import User
from novels.models import Novel, Volume, Chapter, Author, Tag
from constants import DEFAULT_PAGE_NUMBER, ApprovalStatus, UserRole
import warnings
class NovelAdminViewTestCase(TestCase):
    """Base test case for novel admin views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.WEBSITE_ADMIN.value
        )
        
        # Login admin
        self.client.login(username='admin@example.com', password='password123')
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create test author
        self.author = Author.objects.create(
            name="Test Author",
            description="Test author description"
        )
        
        # Create test novels
        self.pending_novel = Novel.objects.create(
            name="Pending Novel",
            summary="Pending summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
            slug="pending-novel"
        )
        
        self.approved_novel = Novel.objects.create(
            name="Approved Novel",
            summary="Approved summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            slug="approved-novel"
        )
        
        # Create tag and assign to approved novel
        self.tag1 = Tag.objects.create(name="Fantasy")
        self.approved_novel.tags.add(self.tag1)

    def test_admin_novels_list_view(self):
        url = reverse("admin:admin_novels")
        response = self.client.get(url, {"page": DEFAULT_PAGE_NUMBER})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/pages/novels_admin.html")
        self.assertIn("page_obj", response.context)
        self.assertContains(response, "Approved Novel")  # chính xác tên novel

    def test_admin_upload_novel_requests_view(self):
        url = reverse("admin:upload_novel_requests")
        response = self.client.get(url, {"page": DEFAULT_PAGE_NUMBER})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/pages/request_novel_admin.html")
        self.assertIn("page_obj", response.context)
        self.assertContains(response, "Pending Novel")  

    def test_admin_novels_filter_by_tag(self):
        url = reverse("admin:admin_novels")
        response = self.client.get(url, {"tag": self.tag1.id})

        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, "Approved Novel")  
        self.assertNotContains(response, "Pending Novel") 
