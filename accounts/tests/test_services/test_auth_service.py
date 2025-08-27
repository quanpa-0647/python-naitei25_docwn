"""
Unit tests for AuthService functionality
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from unittest.mock import Mock, patch

from accounts.services.auth_service import AuthService
from constants import UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class AuthServiceTestCase(TestCase):
    """Base test case for AuthService tests"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value,
            is_active=True
        )
        
        # Create blocked user
        self.blocked_user = User.objects.create_user(
            username='blockeduser',
            email='blocked@example.com',
            password='password123',
            role=UserRole.USER.value,
            is_active=True,
            is_blocked=True
        )
        
        # Create inactive user
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='password123',
            role=UserRole.USER.value,
            is_active=False
        )


class AuthServiceAuthenticateUserTests(AuthServiceTestCase):
    """Test authenticate_user method"""
    
    @patch('accounts.services.auth_service.authenticate')
    @patch('accounts.services.auth_service.login')
    @patch('accounts.services.auth_service.set_session_expiry')
    @patch('accounts.services.auth_service.messages')
    def test_authenticate_user_success(self, mock_messages, mock_set_session, mock_login, mock_authenticate):
        """Test successful user authentication"""
        request = self.factory.post('/login/')
        request.GET = {'next': '/dashboard/'}
        request.session = {}
        
        # Mock successful authentication
        mock_authenticate.return_value = self.user
        
        result = AuthService.authenticate_user(
            request, 
            'test@example.com', 
            'password123',
            remember_me=True
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['redirect_url'], '/dashboard/')
        self.assertIn('Đăng nhập thành công', result['message'])
        
        # Verify method calls
        mock_authenticate.assert_called_once_with(
            request, 
            email='test@example.com', 
            password='password123'
        )
        mock_login.assert_called_once_with(request, self.user)
        mock_set_session.assert_called_once_with(request, True)
        mock_messages.success.assert_called_once()
    
    @patch('accounts.services.auth_service.authenticate')
    def test_authenticate_user_invalid_credentials(self, mock_authenticate):
        """Test authentication with invalid credentials"""
        request = self.factory.post('/login/')
        request.GET = {}
        
        # Mock failed authentication
        mock_authenticate.return_value = None
        
        result = AuthService.authenticate_user(
            request, 
            'wrong@example.com', 
            'wrongpassword'
        )
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('Email hoặc mật khẩu không đúng', result['message'])
        
        mock_authenticate.assert_called_once_with(
            request, 
            email='wrong@example.com', 
            password='wrongpassword'
        )
    
    @patch('accounts.services.auth_service.authenticate')
    def test_authenticate_user_blocked(self, mock_authenticate):
        """Test authentication with blocked user"""
        request = self.factory.post('/login/')
        request.GET = {}
        
        # Mock authentication returning blocked user
        mock_authenticate.return_value = self.blocked_user
        
        result = AuthService.authenticate_user(
            request, 
            'blocked@example.com', 
            'password123'
        )
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('Tài khoản của bạn đã bị khóa', result['message'])
    
    @patch('accounts.services.auth_service.authenticate')
    def test_authenticate_user_inactive(self, mock_authenticate):
        """Test authentication with inactive user"""
        request = self.factory.post('/login/')
        request.GET = {}
        
        # Mock authentication returning inactive user
        mock_authenticate.return_value = self.inactive_user
        
        result = AuthService.authenticate_user(
            request, 
            'inactive@example.com', 
            'password123'
        )
        
        # Verify result
        self.assertFalse(result['success'])
        self.assertIn('Tài khoản chưa được kích hoạt', result['message'])
    
    @patch('accounts.services.auth_service.authenticate')
    @patch('accounts.services.auth_service.login')
    @patch('accounts.services.auth_service.set_session_expiry')
    @patch('accounts.services.auth_service.messages')
    def test_authenticate_user_default_redirect(self, mock_messages, mock_set_session, mock_login, mock_authenticate):
        """Test authentication with default redirect URL"""
        request = self.factory.post('/login/')
        request.GET = {}  # No 'next' parameter
        request.session = {}
        
        # Mock successful authentication
        mock_authenticate.return_value = self.user
        
        result = AuthService.authenticate_user(
            request, 
            'test@example.com', 
            'password123'
        )
        
        # Verify result uses default redirect
        self.assertTrue(result['success'])
        self.assertEqual(result['redirect_url'], settings.LOGIN_REDIRECT_URL)
    
    @patch('accounts.services.auth_service.authenticate')
    @patch('accounts.services.auth_service.login')
    @patch('accounts.services.auth_service.set_session_expiry')
    @patch('accounts.services.auth_service.messages')
    def test_authenticate_user_remember_me_false(self, mock_messages, mock_set_session, mock_login, mock_authenticate):
        """Test authentication without remember me"""
        request = self.factory.post('/login/')
        request.GET = {}
        request.session = {}
        
        # Mock successful authentication
        mock_authenticate.return_value = self.user
        
        result = AuthService.authenticate_user(
            request, 
            'test@example.com', 
            'password123',
            remember_me=False
        )
        
        # Verify remember_me=False is passed
        mock_set_session.assert_called_once_with(request, False)


class AuthServiceLogoutUserTests(AuthServiceTestCase):
    """Test logout_user method"""
    
    @patch('accounts.services.auth_service.logout')
    @patch('accounts.services.auth_service.messages')
    def test_logout_authenticated_user(self, mock_messages, mock_logout):
        """Test logging out authenticated user"""
        request = self.factory.post('/logout/')
        request.user = self.user
        request.GET = {}
        
        # Mock user.get_name() method
        self.user.get_name = Mock(return_value='Test User')
        
        result = AuthService.logout_user(request)
        
        # Verify logout was called
        mock_logout.assert_called_once_with(request)
        mock_messages.success.assert_called_once()
        
        # Verify result uses default logout redirect
        self.assertEqual(result, settings.LOGOUT_REDIRECT_URL)
    
    @patch('accounts.services.auth_service.logout')
    @patch('accounts.services.auth_service.messages')
    def test_logout_anonymous_user(self, mock_messages, mock_logout):
        """Test logging out anonymous user"""
        request = self.factory.post('/logout/')
        request.user = AnonymousUser()
        request.GET = {}
        
        result = AuthService.logout_user(request)
        
        # Verify logout and messages were not called
        mock_logout.assert_not_called()
        mock_messages.success.assert_not_called()
        
        # Should still return redirect URL
        self.assertEqual(result, settings.LOGOUT_REDIRECT_URL)
    
    @patch('accounts.services.auth_service.logout')
    @patch('accounts.services.auth_service.messages')
    def test_logout_with_next_parameter(self, mock_messages, mock_logout):
        """Test logout with next parameter"""
        request = self.factory.post('/logout/')
        request.user = self.user
        request.GET = {'next': '/custom-redirect/'}
        
        # Mock user.get_name() method
        self.user.get_name = Mock(return_value='Test User')
        
        result = AuthService.logout_user(request)
        
        # Verify logout was called
        mock_logout.assert_called_once_with(request)
        
        # Should return custom redirect URL
        self.assertEqual(result, '/custom-redirect/')


class AuthServiceRegisterUserTests(AuthServiceTestCase):
    """Test register_user method"""
    
    def test_register_user_calls_form_save(self):
        """Test register_user calls form.save()"""
        # Create a mock form
        mock_form = Mock()
        mock_form.save.return_value = self.user
        
        result = AuthService.register_user(mock_form)
        
        # Verify form.save() was called
        mock_form.save.assert_called_once()
        
        # Verify the result is the user
        self.assertEqual(result, self.user)
    
    def test_register_user_with_real_form(self):
        """Test register_user with a real form-like object"""
        class MockUserForm:
            def save(self):
                return User.objects.create_user(
                    username='newuser',
                    email='new@example.com',
                    password='newpassword123',
                    role=UserRole.USER.value
                )
        
        form = MockUserForm()
        result = AuthService.register_user(form)
        
        # Verify a user was created
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'newuser')
        self.assertEqual(result.email, 'new@example.com')


class AuthServiceIntegrationTests(AuthServiceTestCase):
    """Test integration scenarios"""
    
    @patch('accounts.services.auth_service.authenticate')
    @patch('accounts.services.auth_service.login')
    @patch('accounts.services.auth_service.set_session_expiry')
    @patch('accounts.services.auth_service.messages')
    def test_full_authentication_flow(self, mock_messages, mock_set_session, mock_login, mock_authenticate):
        """Test complete authentication flow"""
        # Setup mocks
        mock_authenticate.return_value = self.user
        mock_login.return_value = None
        mock_set_session.return_value = None
        
        # Create a request with next parameter
        request = self.factory.post('/login/')
        request.session = {}
        request.GET = {'next': '/profile/'}
        request._messages = Mock()
        
        # Test authentication
        result = AuthService.authenticate_user(
            request,
            'test@example.com',
            'password123',
            remember_me=True
        )
        
        # Should succeed
        self.assertTrue(result['success'])
        self.assertEqual(result['redirect_url'], '/profile/')
        
        # Verify calls
        mock_authenticate.assert_called_once_with(
            request,
            email='test@example.com',
            password='password123'
        )
        mock_login.assert_called_once_with(request, self.user)
        mock_set_session.assert_called_once_with(request, True)
    
    def test_authentication_with_invalid_user_method(self):
        """Test authentication when user.can_login() fails"""
        # Create user with custom can_login method
        special_user = User.objects.create_user(
            username='specialuser',
            email='special@example.com',
            password='password123',
            role=UserRole.USER.value,
            is_active=True
        )
        
        # Mock can_login to return False
        original_can_login = special_user.can_login
        special_user.can_login = Mock(return_value=False)
        special_user.is_blocked = False
        
        request = self.factory.post('/login/')
        request.GET = {}
        
        with patch('accounts.services.auth_service.authenticate') as mock_authenticate:
            mock_authenticate.return_value = special_user
            
            result = AuthService.authenticate_user(
                request,
                'special@example.com',
                'password123'
            )
            
            self.assertFalse(result['success'])
            self.assertIn('Tài khoản chưa được kích hoạt', result['message'])
        
        # Restore original method
        special_user.can_login = original_can_login


class AuthServiceErrorHandlingTests(AuthServiceTestCase):
    """Test error handling and edge cases"""
    
    def test_authenticate_with_none_parameters(self):
        """Test authentication with None parameters"""
        request = self.factory.post('/login/')
        request.GET = {}
        
        with patch('accounts.services.auth_service.authenticate') as mock_authenticate:
            mock_authenticate.return_value = None
            
            result = AuthService.authenticate_user(
                request,
                None,
                None
            )
            
            self.assertFalse(result['success'])
    
    def test_authenticate_with_empty_parameters(self):
        """Test authentication with empty parameters"""
        request = self.factory.post('/login/')
        request.GET = {}
        
        with patch('accounts.services.auth_service.authenticate') as mock_authenticate:
            mock_authenticate.return_value = None
            
            result = AuthService.authenticate_user(
                request,
                '',
                ''
            )
            
            self.assertFalse(result['success'])
    
    def test_logout_with_none_request(self):
        """Test logout with None request should handle gracefully"""
        # This would typically raise an error, but we test the behavior
        with self.assertRaises(AttributeError):
            AuthService.logout_user(None)
    
    def test_register_with_none_form(self):
        """Test register with None form"""
        with self.assertRaises(AttributeError):
            AuthService.register_user(None)
