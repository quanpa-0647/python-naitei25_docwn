import json
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from django.http import HttpResponse
from interactions.models import Notification
from constants import (
    NotificationTypeChoices,
    LIMIT_DEFAULT,
    OFFSET_DEFAULT
)
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()
TEST_CASE_COUNT = 20

class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.notifications = []
        for i in range(TEST_CASE_COUNT):
            notification = Notification.objects.create(
                user=self.user,
                type=NotificationTypeChoices.SYSTEM,
                title=f'Notification {i+1}',
                content=f'Content {i+1}'
            )
            self.notifications.append(notification)
            
    def test_load_more_notifications_login_required(self):
        response = self.client.get('/interactions/ajax/notifications/load_more/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302
        
    @patch('interactions.utils.format_notification')
    def test_load_more_notifications_success(self, mock_format):
        self.client.login(username='test@example.com', password='testpass123')
        
        mock_format.side_effect = lambda n: {
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'is_read': n.is_read
        }
        
        response = self.client.get('/interactions/ajax/notifications/load_more/?offset' + str(OFFSET_DEFAULT) + '&limit=' + str(LIMIT_DEFAULT))
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(len(data['notifications']), LIMIT_DEFAULT)
        self.assertTrue(data['has_more'])
        
    @patch('interactions.utils.format_notification')
    def test_load_more_notifications_default_params(self, mock_format):
        self.client.login(username='test@example.com', password='testpass123')
        
        mock_format.side_effect = lambda n: {'id': n.id, 'title': n.title}
        
        response = self.client.get('/interactions/ajax/notifications/load_more/')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        
    @patch('interactions.utils.format_notification')
    def test_load_more_notifications_no_more(self, mock_format):
        self.client.login(username='test@example.com', password='testpass123')
        
        mock_format.side_effect = lambda n: {'id': n.id, 'title': n.title}
        
        response = self.client.get('/interactions/ajax/notifications/load_more/?offset=' + str(TEST_CASE_COUNT + 1))
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(len(data['notifications']), 0)
        self.assertFalse(data['has_more'])
        
    def test_notification_mark_read_login_required(self):
        notification = self.notifications[0]
        response = self.client.post(f'/interactions/ajax/notifications/{notification.id}/mark_read/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
    def test_notification_mark_read_success(self):
        self.client.login(username='test@example.com', password='testpass123')
        
        notification = self.notifications[0]
        self.assertFalse(notification.is_read)
        
        response = self.client.post(f'/interactions/ajax/notifications/{notification.id}/mark_read/')
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['id'], notification.id)
        
        # Check notification is marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        
    def test_notification_mark_read_wrong_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='other@example.com', password='testpass123')
        
        notification = self.notifications[0]
        
        response = self.client.post(f'/interactions/ajax/notifications/{notification.id}/mark_read/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        
    def test_notification_mark_read_not_found(self):
        self.client.login(username='test@example.com', password='testpass123')
        
        response = self.client.post('/interactions/ajax/notifications/99999/mark_read/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        
    @patch('interactions.views.public.notification_view.create_sse_response')
    def test_sse_stream_login_required(self, mock_sse):
        response = self.client.get('/interactions/sse/stream/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
    @patch('interactions.views.public.notification_view.create_sse_response')
    def test_sse_stream_success(self, mock_sse):
        self.client.force_login(self.user)

        mock_response = HttpResponse("mock stream", content_type="text/event-stream")
        mock_sse.return_value = mock_response

        response = self.client.get('/interactions/sse/stream/')

        mock_sse.assert_called_once_with(self.user.id)
        self.assertEqual(response, mock_response)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "text/event-stream")
