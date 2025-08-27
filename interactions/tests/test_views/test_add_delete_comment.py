from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from interactions.models import Comment
from novels.models import Novel, Author
from constants import UserRole, ApprovalStatus

User = get_user_model()

class AddDeleteCommentViewTests(TestCase):
    def setUp(self):
        # Client chính cho user
        self.client = Client()

        # Tạo user chính
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password123",
            role=UserRole.USER.value,
        )

        # Tạo user khác
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="password123",
            role=UserRole.USER.value,
        )

        # Login user chính
        self.client.login(username="user@example.com", password="password123")

        # Tạo author và novel test
        self.author = Author.objects.create(name="Test Author")
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value,
        )

    def test_add_comment(self):
        """Test adding a top-level comment"""
        url = reverse('interactions:add_comment', args=[self.novel.slug])
        data = {'content': 'This is a test comment'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['content'], 'This is a test comment')
        self.assertIsNone(json_data['parent_id'])
        self.assertTrue(Comment.objects.filter(content='This is a test comment').exists())

    def test_add_reply(self):
        """Test adding a reply to a comment"""
        parent_comment = Comment.objects.create(
            novel=self.novel, user=self.user, content='Parent comment'
        )

        url = reverse('interactions:add_comment', args=[self.novel.slug])
        data = {'content': 'This is a reply', 'parent_comment_id': parent_comment.id}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(int(json_data['parent_id']), parent_comment.id)
        self.assertTrue(Comment.objects.filter(content='This is a reply', parent_comment=parent_comment).exists())

    def test_delete_comment(self):
        """Test deleting own comment"""
        comment = Comment.objects.create(novel=self.novel, user=self.user, content='To be deleted')

        url = reverse('interactions:delete_comment', args=[comment.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])

        comment.refresh_from_db()
        self.assertFalse(comment.is_active)

    def test_add_comment_invalid_form(self):
        """Test submitting empty content"""
        url = reverse('interactions:add_comment', args=[self.novel.slug])
        data = {'content': ''}  # Invalid
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertFalse(json_data['success'])
        self.assertIn('content', json_data['errors'])

    def test_add_comment_not_logged_in(self):
        """Test add comment without login"""
        self.client.logout()
        url = reverse('interactions:add_comment', args=[self.novel.slug])
        data = {'content': 'Test comment'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_delete_comment_not_exists(self):
        """Test deleting a non-existent comment"""
        url = reverse('interactions:delete_comment', args=[9999])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_other_user(self):
        """Test deleting a comment that belongs to another user"""
        comment = Comment.objects.create(novel=self.novel, user=self.other_user, content='Other user comment')
        url = reverse('interactions:delete_comment', args=[comment.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # get_object_or_404 sẽ raise 404 nếu comment.user != request.user
        self.assertEqual(response.status_code, 404)

    def test_add_comment_wrong_method(self):
        url = reverse('interactions:add_comment', args=[self.novel.slug])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 405)
