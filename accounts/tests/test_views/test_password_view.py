from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock
import uuid

from accounts.models import User
from accounts.services import PasswordService
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.change_password_url = reverse('accounts:change_password')

    def test_change_password_view_requires_login(self):
        """Test that change password view requires login"""
        response = self.client.get(self.change_password_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.change_password_url}')

    def test_change_password_view_get(self):
        """Test GET request to change password view"""
        self.client.login(username='test@example.com', password='oldpassword123')
        response = self.client.get(self.change_password_url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'form')
        self.assertTemplateUsed(response, 'accounts/change_password.html')

    @patch('accounts.views.public.password_view.PasswordService.change_password')
    def test_change_password_view_post_success(self, mock_change_password):
        """Test successful password change"""
        mock_change_password.return_value = {
            'success': True,
            'message': 'Đổi mật khẩu thành công!'
        }
        
        self.client.login(username='test@example.com', password='oldpassword123')
        response = self.client.post(self.change_password_url, {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        
        mock_change_password.assert_called_once()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @patch('accounts.views.PasswordService.change_password')
    def test_change_password_view_post_success_with_redirect(self, mock_change_password):
        """Test successful password change with custom redirect"""
        mock_change_password.return_value = {
            'success': True,
            'message': 'Đổi mật khẩu thành công!',
        }
        
        self.client.login(username='test@example.com', password='oldpassword123')
        response = self.client.post(self.change_password_url, {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @patch('accounts.views.PasswordService.change_password')
    def test_change_password_view_post_failure(self, mock_change_password):
        """Test failed password change with mocked service"""
        mock_change_password.return_value = {
            'success': False,
            'message': 'Mật khẩu hiện tại không đúng.'
        }
        
        self.client.login(username='test@example.com', password='oldpassword123')
        response = self.client.post(self.change_password_url, {
            'current_password': 'oldpassword123',   # để form pass
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Mật khẩu hiện tại không đúng.' in str(m) for m in messages))

    def test_change_password_view_invalid_form(self):
        """Test change password with invalid form data"""
        self.client.login(username='test@example.com', password='oldpassword123')
        response = self.client.post(self.change_password_url, {
            'current_password': 'oldpassword123',
            'new_password': 'new',  # Too short
            'confirm_password': 'different'  # Doesn't match
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertTrue(form.errors)


class ForgotPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.forgot_password_url = reverse('accounts:forgot_password')

    def test_forgot_password_view_get(self):
        """Test GET request to forgot password view"""
        response = self.client.get(self.forgot_password_url)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/forgot_password.html')

    @patch('accounts.views.public.password_view.send_password_reset_email')
    @patch('accounts.views.PasswordService.initiate_password_reset')
    def test_forgot_password_view_post_success(self, mock_initiate_reset, mock_send_email):
        """Test successful forgot password request"""
        mock_token = str(uuid.uuid4())
        mock_initiate_reset.return_value = {
            'success': True,
            'message': 'Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.',
            'reset_token': mock_token
        }
        
        response = self.client.post(self.forgot_password_url, {
            'email': 'test@example.com'
        })
        
        mock_initiate_reset.assert_called_once_with('test@example.com')
        mock_send_email.assert_called_once()
        self.assertRedirects(response, reverse('accounts:login'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Liên kết đặt lại mật khẩu' in str(m) for m in messages))

    @patch('accounts.views.PasswordService.initiate_password_reset')
    def test_forgot_password_view_post_failure(self, mock_initiate_reset):
        """Test failed forgot password request"""
        mock_initiate_reset.return_value = {
            'success': False,
            'message': 'Email không tồn tại trong hệ thống.'
        }
        
        response = self.client.post(self.forgot_password_url, {
            'email': 'nonexistent@example.com'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Email không tồn tại' in str(m) for m in messages))

    def test_forgot_password_view_post_empty_email(self):
        """Test forgot password with empty email"""
        response = self.client.post(self.forgot_password_url, {
            'email': ''
        })
        
        self.assertEqual(response.status_code, HTTPStatus.OK)


class ResetPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.token = str(uuid.uuid4())
        
    def test_reset_password_view_invalid_token(self):
        """Test reset password with invalid token"""
        with patch('accounts.views.PasswordService.get_user_by_reset_token', return_value=None):
            response = self.client.get(reverse('accounts:reset_password', kwargs={'token': 'invalid'}))
            
            self.assertRedirects(response, reverse('accounts:forgot_password'))
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any('Liên kết đặt lại mật khẩu không hợp lệ' in str(m) for m in messages))

    def test_reset_password_view_get_valid_token(self):
        """Test GET request with valid token"""
        with patch('accounts.views.PasswordService.get_user_by_reset_token', return_value=self.user):
            response = self.client.get(reverse('accounts:reset_password', kwargs={'token': self.token}))
            
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTemplateUsed(response, 'accounts/reset_password.html')
            self.assertContains(response, self.token)

    @patch('accounts.views.PasswordService.get_user_by_reset_token')
    @patch('accounts.views.PasswordService.reset_password')
    def test_reset_password_view_post_success(self, mock_reset_password, mock_get_user):
        """Test successful password reset"""
        mock_get_user.return_value = self.user
        mock_reset_password.return_value = {
            'success': True,
            'message': 'Đặt lại mật khẩu thành công!'
        }
        
        response = self.client.post(reverse('accounts:reset_password', kwargs={'token': self.token}), {
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        
        mock_reset_password.assert_called_once_with(self.user, 'newpassword123', 'newpassword123')
        self.assertRedirects(response, reverse('accounts:login'))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Đặt lại mật khẩu thành công!' in str(m) for m in messages))

    @patch('accounts.views.PasswordService.get_user_by_reset_token')
    @patch('accounts.views.PasswordService.reset_password')
    def test_reset_password_view_post_failure(self, mock_reset_password, mock_get_user):
        """Test failed password reset"""
        mock_get_user.return_value = self.user
        mock_reset_password.return_value = {
            'success': False,
            'message': 'Mật khẩu mới không khớp.'
        }
        
        response = self.client.post(reverse('accounts:reset_password', kwargs={'token': self.token}), {
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        })
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Mật khẩu mới không khớp.' in str(m) for m in messages))

    def test_reset_password_view_post_invalid_token(self):
        """Test POST request with invalid token"""
        with patch('accounts.views.PasswordService.get_user_by_reset_token', return_value=None):
            response = self.client.post(reverse('accounts:reset_password', kwargs={'token': 'invalid'}), {
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123'
            })
            
            self.assertRedirects(response, reverse('accounts:forgot_password'))
