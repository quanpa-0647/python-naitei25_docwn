from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch

from accounts.forms import ChangePasswordForm
from constants import MIN_PASSWORD_LENGTH
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class ChangePasswordFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )

    def test_form_initialization(self):
        """Test form initializes correctly with user"""
        form = ChangePasswordForm(self.user)
        
        self.assertEqual(form.user, self.user)
        self.assertIn('current_password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('confirm_password', form.fields)

    def test_form_fields_attributes(self):
        """Test form fields have correct attributes"""
        form = ChangePasswordForm(self.user)
        
        # Check current_password field
        current_password_field = form.fields['current_password']
        self.assertEqual(current_password_field.widget.attrs['class'], 'form-control')
        self.assertEqual(current_password_field.widget.attrs['autocomplete'], 'current-password')
        
        # Check new_password field
        new_password_field = form.fields['new_password']
        self.assertEqual(new_password_field.widget.attrs['class'], 'form-control')
        self.assertEqual(new_password_field.widget.attrs['autocomplete'], 'new-password')
        self.assertEqual(new_password_field.min_length, MIN_PASSWORD_LENGTH)
        
        # Check confirm_password field
        confirm_password_field = form.fields['confirm_password']
        self.assertEqual(confirm_password_field.widget.attrs['class'], 'form-control')
        self.assertEqual(confirm_password_field.widget.attrs['autocomplete'], 'new-password')

    def test_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['current_password'], 'oldpassword123')
        self.assertEqual(form.cleaned_data['new_password'], 'newpassword123')
        self.assertEqual(form.cleaned_data['confirm_password'], 'newpassword123')

    def test_clean_current_password_wrong(self):
        """Test validation with wrong current password"""
        form_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('current_password', form.errors)
        self.assertIn('Mật khẩu hiện tại không đúng.', form.errors['current_password'])

    def test_clean_current_password_correct(self):
        """Test validation with correct current password"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        # This should validate the current_password field specifically
        form.is_valid()
        self.assertNotIn('current_password', form.errors)

    @patch('django.contrib.auth.password_validation.validate_password')
    def test_clean_new_password_with_validation_error(self, mock_validate):
        """Test new password validation with Django validators"""
        mock_validate.side_effect = ValidationError(['Ensure this value has at least 8 characters'])
        
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'weak',
            'confirm_password': 'weak'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_new_password_min_length(self):
        """Test new password minimum length validation"""
        short_password = 'a' * (MIN_PASSWORD_LENGTH - 1)
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': short_password,
            'confirm_password': short_password
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_passwords_dont_match(self):
        """Test validation when new passwords don't match"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Mật khẩu mới không khớp.', form.errors['__all__'])

    def test_new_password_same_as_current(self):
        """Test validation when new password is same as current"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'oldpassword123',
            'confirm_password': 'oldpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Mật khẩu mới không được trùng mật khẩu hiện tại.', form.errors['__all__'])

    def test_empty_current_password(self):
        """Test validation with empty current password"""
        form_data = {
            'current_password': '',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('current_password', form.errors)

    def test_empty_new_password(self):
        """Test validation with empty new password"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': '',
            'confirm_password': ''
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_empty_confirm_password(self):
        """Test validation with empty confirm password"""
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': ''
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)

    def test_partial_data_validation(self):
        """Test form validation with partial data"""
        # Test case where only current password matches but new passwords don't
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'different'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        # Should have errors for password mismatch
        self.assertIn('__all__', form.errors)

    @patch('django.contrib.auth.password_validation.validate_password')
    def test_clean_new_password_no_validation_error(self, mock_validate):
        """Test new password validation without Django validators error"""
        mock_validate.return_value = None  # No validation error
        
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'strongnewpassword123',
            'confirm_password': 'strongnewpassword123'
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertTrue(form.is_valid())
        mock_validate.assert_called_once_with('strongnewpassword123', self.user)

    def test_form_help_text(self):
        """Test that form displays help text for password requirements"""
        form = ChangePasswordForm(self.user)
        new_password_field = form.fields['new_password']
        
        expected_help_text = f'Mật khẩu phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự.'
        self.assertIn(str(MIN_PASSWORD_LENGTH), new_password_field.help_text)

    def test_multiple_validation_errors(self):
        """Test form with multiple validation errors"""
        form_data = {
            'current_password': 'wrongpassword',  # Wrong current password
            'new_password': 'new',  # Too short
            'confirm_password': 'different'  # Doesn't match new password
        }
        form = ChangePasswordForm(self.user, data=form_data)
        
        self.assertFalse(form.is_valid())
        # Should have errors for current password, new password length, and mismatch
        self.assertTrue(len(form.errors) > 0)
