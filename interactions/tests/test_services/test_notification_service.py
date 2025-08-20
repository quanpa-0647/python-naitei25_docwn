from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from interactions.models import Notification
from interactions.services import NotificationService
from constants import (
    NotificationTypeChoices,
    LIMIT_DEFAULT,
    OFFSET_DEFAULT
)
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()
TEST_CASE_COUNT = 20

class NotificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        for i in range(TEST_CASE_COUNT):
            Notification.objects.create(
                user=self.user,
                type=NotificationTypeChoices.SYSTEM,
                title=f'Notification {i+1}',
                content=f'Content {i+1}'
            )
            
    def test_get_user_notifications(self):
        notifications = NotificationService.get_user_notifications(
            user=self.user,
            limit=LIMIT_DEFAULT,
            offset= OFFSET_DEFAULT
        )
        
        self.assertEqual(len(notifications), LIMIT_DEFAULT)
        self.assertEqual(notifications[0].title, f'Notification {TEST_CASE_COUNT}')
        
    def test_get_user_notifications_with_offset(self):
        notifications = NotificationService.get_user_notifications(
            user=self.user,
            limit=LIMIT_DEFAULT,
            offset= OFFSET_DEFAULT + LIMIT_DEFAULT
        )
        
        self.assertEqual(len(notifications), LIMIT_DEFAULT)
        self.assertEqual(notifications[0].title, f'Notification {TEST_CASE_COUNT - LIMIT_DEFAULT}')
        
    def test_get_user_notifications_empty_result(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        notifications = NotificationService.get_user_notifications(
            user=other_user,
            limit=LIMIT_DEFAULT,
            offset= TEST_CASE_COUNT + 1
        )
        
        self.assertEqual(len(notifications), 0)
