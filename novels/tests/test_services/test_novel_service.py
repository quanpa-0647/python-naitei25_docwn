"""
Unit tests for NovelService functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch

from novels.services.novel_service import NovelService
from novels.models import Novel, Author, Artist, Category, Tag
from constants import ApprovalStatus, UserRole


User = get_user_model()


class NovelServiceTestCase(TestCase):
    """Base test case for NovelService tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
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
        
        # Create test category
        self.category = Category.objects.create(
            name="Fantasy",
            description="Fantasy novels"
        )
        
        # Create test tag
        self.tag = Tag.objects.create(
            name="Adventure",
            description="Adventure stories"
        )


class NovelServiceCreationTests(NovelServiceTestCase):
    """Test NovelService creation methods"""
    
    def test_create_novel_minimal(self):
        """Test creating novel with minimal data"""
        novel_data = {
            'name': 'Test Novel',
            'summary': 'Test summary',
            'author': self.author
        }
        
        novel = NovelService.create_novel(novel_data, self.user)
        
        self.assertEqual(novel.name, 'Test Novel')
        self.assertEqual(novel.summary, 'Test summary')
        self.assertEqual(novel.author, self.author)
        self.assertEqual(novel.created_by, self.user)
        self.assertEqual(novel.approval_status, ApprovalStatus.PENDING.value)
    
    def test_create_novel_with_categories_and_tags(self):
        """Test creating novel with categories and tags"""
        novel_data = {
            'name': 'Complete Novel',
            'summary': 'Complete summary',
            'author': self.author,
            'categories': [self.category],
            'tags': [self.tag]
        }
        
        novel = NovelService.create_novel(novel_data, self.user)
        
        self.assertIn(self.category, novel.categories.all())
        self.assertIn(self.tag, novel.tags.all())
    
    def test_create_novel_with_artist(self):
        """Test creating novel with artist"""
        artist = Artist.objects.create(
            name="Test Artist",
            description="Test artist description"
        )
        
        novel_data = {
            'name': 'Novel with Artist',
            'summary': 'Test summary',
            'author': self.author,
            'artist': artist
        }
        
        novel = NovelService.create_novel(novel_data, self.user)
        
        self.assertEqual(novel.artist, artist)
    
    @patch('novels.services.novel_service.send_notification')
    def test_create_novel_sends_notification(self, mock_send_notification):
        """Test novel creation sends notification to admins"""
        novel_data = {
            'name': 'Test Novel',
            'summary': 'Test summary',
            'author': self.author
        }
        
        novel = NovelService.create_novel(novel_data, self.user)
        
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'novel_submitted')
        self.assertEqual(call_args['novel_id'], novel.id)


class NovelServiceUpdateTests(NovelServiceTestCase):
    """Test NovelService update methods"""
    
    def setUp(self):
        super().setUp()
        self.novel = Novel.objects.create(
            name="Original Novel",
            summary="Original summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
    
    def test_update_novel_basic_fields(self):
        """Test updating basic novel fields"""
        update_data = {
            'name': 'Updated Novel',
            'summary': 'Updated summary'
        }
        
        updated_novel = NovelService.update_novel(self.novel.id, update_data, self.user)
        
        self.assertEqual(updated_novel.name, 'Updated Novel')
        self.assertEqual(updated_novel.summary, 'Updated summary')
    
    def test_update_novel_categories(self):
        """Test updating novel categories"""
        category2 = Category.objects.create(
            name="Romance",
            description="Romance novels"
        )
        
        update_data = {
            'categories': [self.category, category2]
        }
        
        updated_novel = NovelService.update_novel(self.novel.id, update_data, self.user)
        
        self.assertIn(self.category, updated_novel.categories.all())
        self.assertIn(category2, updated_novel.categories.all())
    
    def test_update_novel_tags(self):
        """Test updating novel tags"""
        tag2 = Tag.objects.create(
            name="Action",
            description="Action stories"
        )
        
        update_data = {
            'tags': [self.tag, tag2]
        }
        
        updated_novel = NovelService.update_novel(self.novel.id, update_data, self.user)
        
        self.assertIn(self.tag, updated_novel.tags.all())
        self.assertIn(tag2, updated_novel.tags.all())
    
    def test_update_novel_permission_check(self):
        """Test update permission checking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        update_data = {'name': 'Unauthorized Update'}
        
        with self.assertRaises(PermissionError):
            NovelService.update_novel(self.novel.id, update_data, other_user)
    
    def test_update_novel_admin_can_update_any(self):
        """Test admin can update any novel"""
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
        
        update_data = {'name': 'Admin Updated Novel'}
        
        updated_novel = NovelService.update_novel(self.novel.id, update_data, admin_user)
        
        self.assertEqual(updated_novel.name, 'Admin Updated Novel')


class NovelServiceApprovalTests(NovelServiceTestCase):
    """Test NovelService approval methods"""
    
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
        
        self.novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
    
    @patch('novels.services.novel_service.send_notification')
    def test_approve_novel(self, mock_send_notification):
        """Test approving a novel"""
        approved_novel = NovelService.approve_novel(self.novel.id, self.admin_user)
        
        self.assertEqual(approved_novel.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(approved_novel.approved_by, self.admin_user)
        self.assertIsNotNone(approved_novel.approved_at)
        
        # Check notification sent to novel creator
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'novel_approved')
        self.assertEqual(call_args['user'], self.user)
    
    @patch('novels.services.novel_service.send_notification')
    def test_reject_novel(self, mock_send_notification):
        """Test rejecting a novel"""
        rejection_reason = "Content does not meet quality standards"
        
        rejected_novel = NovelService.reject_novel(
            self.novel.id, 
            self.admin_user, 
            rejection_reason
        )
        
        self.assertEqual(rejected_novel.approval_status, ApprovalStatus.REJECTED.value)
        self.assertEqual(rejected_novel.rejected_reason, rejection_reason)
        self.assertEqual(rejected_novel.approved_by, self.admin_user)
        self.assertIsNotNone(rejected_novel.approved_at)
        
        # Check notification sent to novel creator
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'novel_rejected')
        self.assertEqual(call_args['user'], self.user)
        self.assertEqual(call_args['reason'], rejection_reason)
    
    def test_approve_novel_permission_check(self):
        """Test only admins can approve novels"""
        with self.assertRaises(PermissionError):
            NovelService.approve_novel(self.novel.id, self.user)
    
    def test_reject_novel_permission_check(self):
        """Test only admins can reject novels"""
        with self.assertRaises(PermissionError):
            NovelService.reject_novel(self.novel.id, self.user, "Test reason")


class NovelServiceQueryTests(NovelServiceTestCase):
    """Test NovelService query methods"""
    
    def setUp(self):
        super().setUp()
        # Create test novels
        self.approved_novel = Novel.objects.create(
            name="Approved Novel",
            summary="Approved summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        self.pending_novel = Novel.objects.create(
            name="Pending Novel",
            summary="Pending summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        
        self.rejected_novel = Novel.objects.create(
            name="Rejected Novel",
            summary="Rejected summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.REJECTED.value
        )
    
    def test_get_published_novels(self):
        """Test getting published novels"""
        published_novels = NovelService.get_published_novels()
        
        self.assertIn(self.approved_novel, published_novels)
        self.assertNotIn(self.pending_novel, published_novels)
        self.assertNotIn(self.rejected_novel, published_novels)
    
    def test_get_novels_by_category(self):
        """Test getting novels by category"""
        self.approved_novel.categories.add(self.category)
        
        novels_by_category = NovelService.get_novels_by_category(self.category)
        
        self.assertIn(self.approved_novel, novels_by_category)
        self.assertNotIn(self.pending_novel, novels_by_category)
    
    def test_get_novels_by_tag(self):
        """Test getting novels by tag"""
        self.approved_novel.tags.add(self.tag)
        
        novels_by_tag = NovelService.get_novels_by_tag(self.tag)
        
        self.assertIn(self.approved_novel, novels_by_tag)
        self.assertNotIn(self.pending_novel, novels_by_tag)
    
    def test_search_novels(self):
        """Test searching novels by title and content"""
        search_results = NovelService.search_novels("Approved")
        
        self.assertIn(self.approved_novel, search_results)
        self.assertNotIn(self.pending_novel, search_results)
        self.assertNotIn(self.rejected_novel, search_results)
    
    def test_get_trending_novels(self):
        """Test getting trending novels"""
        # Mock view counts
        self.approved_novel.view_count = 1000
        self.approved_novel.save()
        
        trending_novels = NovelService.get_trending_novels(limit=5)
        
        self.assertIn(self.approved_novel, trending_novels)
    
    def test_get_user_novels(self):
        """Test getting novels by user"""
        user_novels = NovelService.get_user_novels(self.user)
        
        self.assertIn(self.approved_novel, user_novels)
        self.assertIn(self.pending_novel, user_novels)
        self.assertIn(self.rejected_novel, user_novels)
    
    def test_get_pending_novels_for_review(self):
        """Test getting novels pending review"""
        pending_novels = NovelService.get_pending_novels_for_review()
        
        self.assertIn(self.pending_novel, pending_novels)
        self.assertNotIn(self.approved_novel, pending_novels)
        self.assertNotIn(self.rejected_novel, pending_novels)


class NovelServiceStatisticsTests(NovelServiceTestCase):
    """Test NovelService statistics methods"""
    
    def setUp(self):
        super().setUp()
        self.novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
    
    @patch('novels.services.novel_service.update_view_count')
    def test_increment_view_count(self, mock_update_view_count):
        """Test incrementing novel view count"""
        NovelService.increment_view_count(self.novel.id)
        
        mock_update_view_count.assert_called_once_with(self.novel.id)
    
    def test_get_novel_statistics(self):
        """Test getting novel statistics"""
        stats = NovelService.get_novel_statistics(self.novel.id)
        
        self.assertIn('view_count', stats)
        self.assertIn('chapter_count', stats)
        self.assertIn('word_count', stats)
        self.assertIn('rating_average', stats)
        self.assertIn('rating_count', stats)
    
    def test_get_reading_progress(self):
        """Test getting user reading progress"""
        progress = NovelService.get_reading_progress(self.novel.id, self.user)
        
        self.assertIn('current_chapter', progress)
        self.assertIn('total_chapters', progress)
        self.assertIn('progress_percentage', progress)


class NovelServiceValidationTests(NovelServiceTestCase):
    """Test NovelService validation methods"""
    
    def test_validate_novel_data_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_data = {
            'summary': 'Test summary'
            # Missing name and author
        }
        
        with self.assertRaises(ValueError):
            NovelService.validate_novel_data(invalid_data)
    
    def test_validate_novel_data_invalid_name(self):
        """Test validation with invalid name"""
        invalid_data = {
            'name': '',  # Empty name
            'summary': 'Test summary',
            'author': self.author
        }
        
        with self.assertRaises(ValueError):
            NovelService.validate_novel_data(invalid_data)
    
    def test_validate_novel_data_invalid_summary(self):
        """Test validation with invalid summary"""
        invalid_data = {
            'name': 'Test Novel',
            'summary': '',  # Empty summary
            'author': self.author
        }
        
        with self.assertRaises(ValueError):
            NovelService.validate_novel_data(invalid_data)
    
    def test_validate_novel_data_valid(self):
        """Test validation with valid data"""
        valid_data = {
            'name': 'Test Novel',
            'summary': 'Test summary',
            'author': self.author
        }
        
        # Should not raise any exception
        NovelService.validate_novel_data(valid_data)
    
    def test_check_duplicate_novel_name(self):
        """Test checking for duplicate novel names"""
        Novel.objects.create(
            name="Existing Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user
        )
        
        # Should raise exception for duplicate name
        with self.assertRaises(ValueError):
            NovelService.check_duplicate_novel_name("Existing Novel")
        
        # Should not raise exception for unique name
        NovelService.check_duplicate_novel_name("Unique Novel")


class NovelServiceDeleteTests(NovelServiceTestCase):
    """Test NovelService deletion methods"""
    
    def setUp(self):
        super().setUp()
        self.novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.PENDING.value
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
    
    def test_soft_delete_novel_by_owner(self):
        """Test soft deleting novel by owner"""
        deleted_novel = NovelService.soft_delete_novel(self.novel.id, self.user)
        
        self.assertTrue(deleted_novel.is_deleted)
        self.assertIsNotNone(deleted_novel.deleted_at)
    
    def test_soft_delete_novel_by_admin(self):
        """Test soft deleting novel by admin"""
        deleted_novel = NovelService.soft_delete_novel(self.novel.id, self.admin_user)
        
        self.assertTrue(deleted_novel.is_deleted)
        self.assertIsNotNone(deleted_novel.deleted_at)
    
    def test_soft_delete_novel_permission_check(self):
        """Test soft delete permission checking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        with self.assertRaises(PermissionError):
            NovelService.soft_delete_novel(self.novel.id, other_user)
    
    def test_restore_novel(self):
        """Test restoring soft deleted novel"""
        # First soft delete
        NovelService.soft_delete_novel(self.novel.id, self.user)
        
        # Then restore
        restored_novel = NovelService.restore_novel(self.novel.id, self.admin_user)
        
        self.assertFalse(restored_novel.is_deleted)
        self.assertIsNone(restored_novel.deleted_at)
    
    def test_restore_novel_permission_check(self):
        """Test restore novel permission checking"""
        # Soft delete first
        NovelService.soft_delete_novel(self.novel.id, self.user)
        
        # User cannot restore
        with self.assertRaises(PermissionError):
            NovelService.restore_novel(self.novel.id, self.user)
