# tests/test_profile_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.conf import settings
from unittest.mock import patch
from datetime import date

from accounts.models import UserProfile
from constants import Gender

User = get_user_model()


class UserProfileModelTest(TestCase):
    def setUp(self):
        """Thiết lập dữ liệu test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_auto_creation(self):
        """Test profile được tạo tự động khi tạo user"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_str_method(self):
        """Test phương thức __str__ của profile"""
        expected = f"Profile of {self.user.username}"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_get_name_with_display_name(self):
        """Test get_name() khi có display_name"""
        self.user.profile.display_name = "Tên Hiển Thị"
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_name(), "Tên Hiển Thị")
    
    def test_get_name_without_display_name(self):
        """Test get_name() khi không có display_name"""
        self.assertEqual(self.user.profile.get_name(), self.user.username)
    
    @patch('django.conf.settings.DEFAULT_AVATAR_URL', 'http://example.com/default.jpg')
    def test_get_avatar_without_url(self):
        """Test get_avatar() khi không có avatar_url"""
        self.assertEqual(
            self.user.profile.get_avatar(), 
            'http://example.com/default.jpg'
        )
    
    def test_get_avatar_with_url(self):
        """Test get_avatar() khi có avatar_url"""
        test_url = "http://example.com/avatar.jpg"
        self.user.profile.avatar_url = test_url
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_avatar(), test_url)
    
    def test_get_gender_display_male(self):
        """Test hiển thị giới tính Nam"""
        self.user.profile.gender = Gender.MALE.value
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_gender_display(), "Nam")
    
    def test_get_gender_display_female(self):
        """Test hiển thị giới tính Nữ"""
        self.user.profile.gender = Gender.FEMALE.value
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_gender_display(), "Nữ")
    
    def test_get_gender_display_other(self):
        """Test hiển thị giới tính Khác"""
        self.user.profile.gender = Gender.OTHER.value
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_gender_display(), "Khác")
    
    def test_get_gender_display_none(self):
        """Test hiển thị giới tính khi không có giá trị"""
        self.assertEqual(self.user.profile.get_gender_display(), "Không xác định")
    
    def test_has_external_avatar_true(self):
        """Test has_external_avatar() trả về True khi có avatar_url"""
        self.user.profile.avatar_url = "http://example.com/avatar.jpg"
        self.user.profile.save()
        self.assertTrue(self.user.profile.has_external_avatar())
    
    def test_has_external_avatar_false(self):
        """Test has_external_avatar() trả về False khi không có avatar_url"""
        self.assertFalse(self.user.profile.has_external_avatar())
    
    def test_profile_fields_optional(self):
        """Test các field optional có thể để trống"""
        profile = self.user.profile
        profile.display_name = None
        profile.gender = None
        profile.birthday = None
        profile.avatar_url = None
        profile.description = None
        profile.interest = None
        profile.save()
        
        # Không nên có lỗi
        self.assertIsNone(profile.display_name)
        self.assertIsNone(profile.gender)
        self.assertIsNone(profile.birthday)
    
    def test_profile_with_all_fields(self):
        """Test profile với đầy đủ thông tin"""
        profile = self.user.profile
        profile.display_name = "Nguyễn Văn A"
        profile.gender = Gender.MALE.value
        profile.birthday = date(1990, 1, 1)
        profile.avatar_url = "http://example.com/avatar.jpg"
        profile.description = "Mô tả về bản thân"
        profile.interest = "Đọc sách, xem phim"
        profile.is_locked = False
        profile.save()
        
        self.assertEqual(profile.display_name, "Nguyễn Văn A")
        self.assertEqual(profile.gender, Gender.MALE.value)
        self.assertEqual(profile.birthday, date(1990, 1, 1))
        self.assertEqual(profile.avatar_url, "http://example.com/avatar.jpg")
        self.assertEqual(profile.description, "Mô tả về bản thân")
        self.assertEqual(profile.interest, "Đọc sách, xem phim")
        self.assertFalse(profile.is_locked)
    
    def test_profile_user_deletion_restriction(self):
        """Test profile không cho phép xóa user (RESTRICT)"""
        profile_id = self.user.profile.id
        
        # Thử xóa user sẽ raise error do RESTRICT
        with self.assertRaises(Exception):
            self.user.delete()
        
        # Profile vẫn tồn tại
        self.assertTrue(UserProfile.objects.filter(id=profile_id).exists())
    
    def test_profile_timestamps(self):
        """Test timestamps được tạo và cập nhật đúng"""
        profile = self.user.profile
        created_at = profile.created_at
        updated_at = profile.updated_at
        
        # Cập nhật profile
        profile.display_name = "New Name"
        profile.save()
        
        # created_at không đổi, updated_at thay đổi
        self.assertEqual(profile.created_at, created_at)
        self.assertGreater(profile.updated_at, updated_at)


class UserProfileSignalTest(TestCase):
    """Test Django signals cho UserProfile"""
    
    def test_profile_created_on_user_creation(self):
        """Test profile được tạo tự động khi tạo user mới"""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_profile_saved_on_user_save(self):
        """Test profile được save khi user được save"""
        user = User.objects.create_user(
            username='saveuser',
            email='save@example.com', 
            password='password123'
        )
        
        # Thay đổi user
        user.email = 'newemail@example.com'
        user.save()
        
        # Profile vẫn tồn tại và được save
        user.refresh_from_db()
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile.updated_at)
