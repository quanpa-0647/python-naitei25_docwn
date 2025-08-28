from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from interactions.models import Notification
from constants import NotificationTypeChoices
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationTypeChoices.SYSTEM,
            title='Test Notification',
            content='Test content'
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.content, 'Test content')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
        
    def test_notification_str_method(self):
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationTypeChoices.SYSTEM,
            title='Test Notification',
            content='Test content'
        )
        
        expected_str = f"Test Notification - {self.user.username}"
        self.assertEqual(str(notification), expected_str)
        
    def test_mark_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationTypeChoices.SYSTEM,
            title='Test Notification',
            content='Test content'
        )
        
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
