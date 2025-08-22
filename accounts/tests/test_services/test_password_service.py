from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock
import uuid

from accounts.services import PasswordService
from accounts.models import User
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class PasswordServiceTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )

    def test_change_password_wrong_current_password(self):
        """Test change password with wrong current password"""
        request = self.factory.post('/')
        request.user = self.user
        
        result = PasswordService.change_password(
            request=request,
            current_password='wrongpassword',
            new_password='newpassword123',
            confirm_password='newpassword123',
            keep_session=True
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Mật khẩu hiện tại không đúng', result['message'])

    @patch('accounts.services.validate_password')
    def test_change_password_invalid_new_password(self, mock_validate):
        """Test change password with invalid new password"""
        mock_validate.return_value = {
            'valid': False,
            'message': 'Mật khẩu quá yếu'
        }
        
        request = self.factory.post('/')
        request.user = self.user
        
        result = PasswordService.change_password(
            request=request,
            current_password='oldpassword123',
            new_password='weak',
            confirm_password='weak',
            keep_session=True
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Mật khẩu phải có ít nhất 8 ký tự.')

    def test_change_password_same_as_current(self):
        """Test change password when new password same as current"""
        request = self.factory.post('/')
        request.user = self.user
        
        with patch('accounts.services.validate_password') as mock_validate:
            mock_validate.return_value = {'valid': True}
            
            result = PasswordService.change_password(
                request=request,
                current_password='oldpassword123',
                new_password='oldpassword123',
                confirm_password='oldpassword123',
                keep_session=True
            )
        
        self.assertFalse(result['success'])
        self.assertIn('không được trùng mật khẩu hiện tại', result['message'])

    @patch('accounts.services.password_service.validate_password')
    @patch('accounts.services.password_service.update_session_auth_hash')
    @patch('django.contrib.messages.success')
    def test_change_password_success_keep_session(self, mock_messages, mock_update_session, mock_validate):
        """Test successful password change keeping session"""
        mock_validate.return_value = {'valid': True}
        
        request = self.factory.post('/')
        request.user = self.user
        
        result = PasswordService.change_password(
            request=request,
            current_password='oldpassword123',
            new_password='newpassword123',
            confirm_password='newpassword123',
            keep_session=True
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Đổi mật khẩu thành công', result['message'])
        self.assertNotIn('redirect_url', result)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        
        # Verify session was updated
        mock_update_session.assert_called_once_with(request, self.user)
        mock_messages.assert_called_once()


    @patch('accounts.services.validate_password')
    @patch('django.contrib.messages.success')
    def test_change_password_success_logout(self, mock_messages, mock_validate):
        """Test successful password change with logout"""
        mock_validate.return_value = {'valid': True}
        
        request = self.factory.post('/')
        request.user = self.user
        
        result = PasswordService.change_password(
            request=request,
            current_password='oldpassword123',
            new_password='newpassword123',
            confirm_password='newpassword123',
            keep_session=False
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Đổi mật khẩu thành công', result['message'])
        self.assertEqual(result['redirect_url'], 'accounts:login')
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_initiate_password_reset_user_not_found(self):
        """Test password reset initiation with non-existent email"""
        result = PasswordService.initiate_password_reset('nonexistent@example.com')
        
        self.assertFalse(result['success'])
        self.assertIn('Email không tồn tại', result['message'])

    def test_initiate_password_reset_success(self):
        """Test successful password reset initiation"""
        result = PasswordService.initiate_password_reset('test@example.com')
        
        self.assertTrue(result['success'])
        self.assertIn('Liên kết đặt lại mật khẩu', result['message'])
        self.assertIn('reset_token', result)
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.password_reset_token)
        self.assertIsNotNone(self.user.password_reset_expires)
        
        # Verify token expiry is approximately 1 hour from now
        expected_expiry = timezone.now() + timedelta(hours=1)
        time_diff = abs((self.user.password_reset_expires - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute
        
        # Verify reset token can be verified
        reset_token = result['reset_token']
        self.assertTrue(check_password(reset_token, self.user.password_reset_token))

    def test_get_user_by_reset_token_no_token(self):
        """Test getting user with no token"""
        result = PasswordService.get_user_by_reset_token(None)
        self.assertIsNone(result)
        
        result = PasswordService.get_user_by_reset_token('')
        self.assertIsNone(result)

    def test_get_user_by_reset_token_invalid_token(self):
        """Test getting user with invalid token"""
        # Set up user with reset token
        token_plain = str(uuid.uuid4())
        self.user.password_reset_token = make_password(token_plain)
        self.user.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.user.save()
        
        # Try with wrong token
        result = PasswordService.get_user_by_reset_token('wrongtoken')
        self.assertIsNone(result)

    def test_get_user_by_reset_token_expired_token(self):
        """Test getting user with expired token"""
        token_plain = str(uuid.uuid4())
        self.user.password_reset_token = make_password(token_plain)
        self.user.password_reset_expires = timezone.now() - timedelta(hours=1)  # Expired
        self.user.save()
        
        result = PasswordService.get_user_by_reset_token(token_plain)
        self.assertIsNone(result)

    def test_get_user_by_reset_token_no_expiry(self):
        """Test getting user with no reset expiry set"""
        token_plain = str(uuid.uuid4())
        self.user.password_reset_token = make_password(token_plain)
        self.user.password_reset_expires = None
        self.user.save()
        
        result = PasswordService.get_user_by_reset_token(token_plain)
        self.assertIsNone(result)

    def test_get_user_by_reset_token_success(self):
        """Test getting user with valid token"""
        token_plain = str(uuid.uuid4())
        self.user.password_reset_token = make_password(token_plain)
        self.user.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.user.save()
        
        result = PasswordService.get_user_by_reset_token(token_plain)
        self.assertEqual(result, self.user)

    def test_get_user_by_reset_token_multiple_users(self):
        """Test getting user when multiple users have reset tokens"""
        # Create another user with different token
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        token1_plain = str(uuid.uuid4())
        token2_plain = str(uuid.uuid4())
        
        # Set up both users with reset tokens
        self.user.password_reset_token = make_password(token1_plain)
        self.user.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.user.save()
        
        user2.password_reset_token = make_password(token2_plain)
        user2.password_reset_expires = timezone.now() + timedelta(hours=1)
        user2.save()
        
        # Test getting correct user for each token
        result1 = PasswordService.get_user_by_reset_token(token1_plain)
        result2 = PasswordService.get_user_by_reset_token(token2_plain)
        
        self.assertEqual(result1, self.user)
        self.assertEqual(result2, user2)

    @patch('accounts.services.validate_password')
    def test_reset_password_invalid_password(self, mock_validate):
        """Test password reset with invalid password"""
        mock_validate.return_value = {
            'valid': False,
            'message': 'Mật khẩu không hợp lệ'
        }
        
        result = PasswordService.reset_password(
            user=self.user,
            new_password='weak',
            confirm_password='different'
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Mật khẩu mới không khớp.')

    @patch('accounts.services.password_service.validate_password')
    def test_reset_password_success(self, mock_validate):
        """Test successful password reset"""
        mock_validate.return_value = {'valid': True}
        
        # Set up user with reset token
        token_plain = str(uuid.uuid4())
        self.user.password_reset_token = make_password(token_plain)
        self.user.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.user.save()
        
        old_password_hash = self.user.password
        
        result = PasswordService.reset_password(
            user=self.user,
            new_password='newpassword123',
            confirm_password='newpassword123'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Đặt lại mật khẩu thành công', result['message'])
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertNotEqual(self.user.password, old_password_hash)
        self.assertIsNone(self.user.password_reset_token)
        self.assertIsNone(self.user.password_reset_expires)

    def test_reset_password_clears_token_data(self):
        """Test that reset password clears token and expiry"""
        with patch('accounts.services.validate_password') as mock_validate:
            mock_validate.return_value = {'valid': True}
            
            # Set up user with reset token
            self.user.password_reset_token = make_password(str(uuid.uuid4()))
            self.user.password_reset_expires = timezone.now() + timedelta(hours=1)
            self.user.save()
            
            PasswordService.reset_password(
                user=self.user,
                new_password='newpassword123',
                confirm_password='newpassword123'
            )
            
            # Verify token data was cleared
            self.user.refresh_from_db()
            self.assertIsNone(self.user.password_reset_token)
            self.assertIsNone(self.user.password_reset_expires)

    def test_initiate_password_reset_overwrites_existing_token(self):
        """Test that initiating password reset overwrites existing token"""
        # Set up user with existing reset token
        old_token = str(uuid.uuid4())
        self.user.password_reset_token = make_password(old_token)
        self.user.password_reset_expires = timezone.now() + timedelta(minutes=30)
        self.user.save()
        
        # Initiate new password reset
        result = PasswordService.initiate_password_reset('test@example.com')
        
        self.assertTrue(result['success'])
        
        # Verify new token overwrote old one
        self.user.refresh_from_db()
        new_token = result['reset_token']
        self.assertTrue(check_password(new_token, self.user.password_reset_token))
        self.assertFalse(check_password(old_token, self.user.password_reset_token))

    def test_password_service_edge_cases(self):
        """Test various edge cases for password service methods"""
        # Test with user that doesn't exist in get_user_by_reset_token
        non_existent_token = str(uuid.uuid4())
        result = PasswordService.get_user_by_reset_token(non_existent_token)
        self.assertIsNone(result)
        
        # Test change_password with None values
        request = self.factory.post('/')
        request.user = self.user
        
        with patch('accounts.services.validate_password') as mock_validate:
            mock_validate.return_value = {'valid': True}
            
            # Test with empty strings
            result = PasswordService.change_password(
                request=request,
                current_password='',
                new_password='newpass123',
                confirm_password='newpass123',
                keep_session=True
            )
            self.assertFalse(result['success'])

    def test_concurrent_password_reset_requests(self):
        """Test handling multiple password reset requests"""
        # First reset request
        result1 = PasswordService.initiate_password_reset('test@example.com')
        token1 = result1['reset_token']
        
        # Second reset request (should overwrite first)
        result2 = PasswordService.initiate_password_reset('test@example.com')
        token2 = result2['reset_token']
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertNotEqual(token1, token2)
        
        # Only second token should work
        user_from_token1 = PasswordService.get_user_by_reset_token(token1)
        user_from_token2 = PasswordService.get_user_by_reset_token(token2)
        
        self.assertIsNone(user_from_token1)
        self.assertEqual(user_from_token2, self.user)
