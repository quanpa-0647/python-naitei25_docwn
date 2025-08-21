"""
Unit tests for ChapterService functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock

from novels.services.chapter_service import ChapterService
from novels.models import Novel, Volume, Chapter, Author, Chunk
from constants import ApprovalStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")


User = get_user_model()


class ChapterServiceTestCase(TestCase):
    """Base test case for ChapterService tests"""
    
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
        
        # Create test novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        # Create test volume
        self.volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )


class ChapterServiceCreationTests(ChapterServiceTestCase):
    """Test ChapterService creation methods"""
    
    @patch('novels.services.chapter_service.ChunkManager.create_chunks')
    def test_create_chapter_minimal(self, mock_create_chunks):
        """Test creating chapter with minimal data"""
        mock_create_chunks.return_value = [
            Mock(content="Test content", word_count=2)
        ]
        
        chapter_data = {
            'title': 'Test Chapter',
            'content': 'Test content',
            'volume': self.volume
        }
        
        chapter = ChapterService.create_chapter(chapter_data, self.user)
        
        self.assertEqual(chapter.title, 'Test Chapter')
        self.assertEqual(chapter.volume, self.volume)
        self.assertEqual(chapter.position, 1)  # First chapter in volume
        self.assertFalse(chapter.approved)
        
        # Check that chunks were created
        mock_create_chunks.assert_called_once_with('Test content', chapter)
    
    @patch('novels.services.chapter_service.ChunkManager.create_chunks')
    def test_create_chapter_with_position(self, mock_create_chunks):
        """Test creating chapter with specific position"""
        mock_create_chunks.return_value = [
            Mock(content="Test content", word_count=2)
        ]
        
        # Create existing chapter
        Chapter.objects.create(
            volume=self.volume,
            title="Existing Chapter",
            position=1
        )
        
        chapter_data = {
            'title': 'New Chapter',
            'content': 'New content',
            'volume': self.volume,
            'position': 2
        }
        
        chapter = ChapterService.create_chapter(chapter_data, self.user)
        
        self.assertEqual(chapter.position, 2)
    
    @patch('novels.services.chapter_service.ChunkManager.create_chunks')
    def test_create_chapter_auto_position(self, mock_create_chunks):
        """Test automatic position assignment"""
        mock_create_chunks.return_value = [
            Mock(content="Test content", word_count=2)
        ]
        
        # Create existing chapters
        Chapter.objects.create(volume=self.volume, title="Chapter 1", position=1)
        Chapter.objects.create(volume=self.volume, title="Chapter 2", position=2)
        
        chapter_data = {
            'title': 'Auto Position Chapter',
            'content': 'Auto content',
            'volume': self.volume
        }
        
        chapter = ChapterService.create_chapter(chapter_data, self.user)
        
        self.assertEqual(chapter.position, 3)  # Auto-assigned next position
    
    @patch('novels.services.chapter_service.send_notification')
    @patch('novels.services.chapter_service.ChunkManager.create_chunks')
    def test_create_chapter_sends_notification(self, mock_create_chunks, mock_send_notification):
        """Test chapter creation sends notification"""
        mock_create_chunks.return_value = [
            Mock(content="Test content", word_count=2)
        ]
        
        chapter_data = {
            'title': 'Test Chapter',
            'content': 'Test content',
            'volume': self.volume
        }
        
        chapter = ChapterService.create_chapter(chapter_data, self.user)
        
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'chapter_submitted')
        self.assertEqual(call_args['chapter_id'], chapter.id)


class ChapterServiceUpdateTests(ChapterServiceTestCase):
    """Test ChapterService update methods"""
    
    def setUp(self):
        super().setUp()
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Original Chapter",
            position=1
        )
        
        # Create original chunks
        Chunk.objects.create(
            chapter=self.chapter,
            content="Original content",
            position=1,
            word_count=2
        )
    
    @patch('novels.services.chapter_service.ChunkManager.update_chunks')
    def test_update_chapter_title_only(self, mock_update_chunks):
        """Test updating only chapter title"""
        update_data = {
            'title': 'Updated Chapter Title'
        }
        
        updated_chapter = ChapterService.update_chapter(
            self.chapter.id, 
            update_data, 
            self.user
        )
        
        self.assertEqual(updated_chapter.title, 'Updated Chapter Title')
        # Content update should not be called if no content provided
        mock_update_chunks.assert_not_called()
    
    @patch('novels.services.chapter_service.ChunkManager.update_chunks')
    def test_update_chapter_content(self, mock_update_chunks):
        """Test updating chapter content"""
        mock_update_chunks.return_value = [
            Mock(content="Updated content", word_count=2)
        ]
        
        update_data = {
            'title': 'Updated Chapter',
            'content': 'Updated content'
        }
        
        updated_chapter = ChapterService.update_chapter(
            self.chapter.id, 
            update_data, 
            self.user
        )
        
        self.assertEqual(updated_chapter.title, 'Updated Chapter')
        mock_update_chunks.assert_called_once_with('Updated content', self.chapter)
    
    def test_update_chapter_permission_check(self):
        """Test update permission checking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        update_data = {'title': 'Unauthorized Update'}
        
        with self.assertRaises(PermissionError):
            ChapterService.update_chapter(self.chapter.id, update_data, other_user)
    
    def test_update_chapter_admin_can_update_any(self):
        """Test admin can update any chapter"""
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
        
        update_data = {'title': 'Admin Updated Chapter'}
        
        updated_chapter = ChapterService.update_chapter(
            self.chapter.id, 
            update_data, 
            admin_user
        )
        
        self.assertEqual(updated_chapter.title, 'Admin Updated Chapter')


class ChapterServiceApprovalTests(ChapterServiceTestCase):
    """Test ChapterService approval methods"""
    
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
        
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1,
            approved=False
        )
    
    @patch('novels.services.chapter_service.send_notification')
    def test_approve_chapter(self, mock_send_notification):
        """Test approving a chapter"""
        approved_chapter = ChapterService.approve_chapter(
            self.chapter.id, 
            self.admin_user
        )
        
        self.assertTrue(approved_chapter.approved)
        self.assertEqual(approved_chapter.approved_by, self.admin_user)
        self.assertIsNotNone(approved_chapter.approved_at)
        
        # Check notification sent to chapter creator
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'chapter_approved')
    
    @patch('novels.services.chapter_service.send_notification')
    def test_reject_chapter(self, mock_send_notification):
        """Test rejecting a chapter"""
        rejection_reason = "Content quality issues"
        
        rejected_chapter = ChapterService.reject_chapter(
            self.chapter.id, 
            self.admin_user, 
            rejection_reason
        )
        
        self.assertFalse(rejected_chapter.approved)
        self.assertEqual(rejected_chapter.rejected_reason, rejection_reason)
        self.assertEqual(rejected_chapter.approved_by, self.admin_user)
        self.assertIsNotNone(rejected_chapter.approved_at)
        
        # Check notification sent to chapter creator
        mock_send_notification.assert_called_once()
        call_args = mock_send_notification.call_args[1]
        self.assertEqual(call_args['type'], 'chapter_rejected')
        self.assertEqual(call_args['reason'], rejection_reason)
    
    def test_approve_chapter_permission_check(self):
        """Test only admins can approve chapters"""
        with self.assertRaises(PermissionError):
            ChapterService.approve_chapter(self.chapter.id, self.user)
    
    def test_reject_chapter_permission_check(self):
        """Test only admins can reject chapters"""
        with self.assertRaises(PermissionError):
            ChapterService.reject_chapter(self.chapter.id, self.user, "Test reason")


class ChapterServiceQueryTests(ChapterServiceTestCase):
    """Test ChapterService query methods"""
    
    def setUp(self):
        super().setUp()
        # Create test chapters
        self.approved_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Approved Chapter",
            position=1,
            approved=True,
            is_hidden=False
        )
        
        self.pending_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Pending Chapter",
            position=2,
            approved=False,
            is_hidden=False
        )
        
        self.hidden_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Hidden Chapter",
            position=3,
            approved=True,
            is_hidden=True
        )
    
    def test_get_published_chapters(self):
        """Test getting published chapters"""
        published_chapters = ChapterService.get_published_chapters(self.volume)
        
        self.assertIn(self.approved_chapter, published_chapters)
        self.assertNotIn(self.pending_chapter, published_chapters)
        self.assertNotIn(self.hidden_chapter, published_chapters)
    
    def test_get_chapter_with_content(self):
        """Test getting chapter with content"""
        # Create chunks for the chapter
        Chunk.objects.create(
            chapter=self.approved_chapter,
            content="First chunk",
            position=1,
            word_count=2
        )
        
        Chunk.objects.create(
            chapter=self.approved_chapter,
            content="Second chunk",
            position=2,
            word_count=2
        )
        
        chapter_with_content = ChapterService.get_chapter_with_content(
            self.approved_chapter.id
        )
        
        self.assertEqual(chapter_with_content, self.approved_chapter)
        # Check content is properly loaded
        content = chapter_with_content.get_content()
        self.assertIn("First chunk", content)
        self.assertIn("Second chunk", content)
    
    def test_get_next_chapter(self):
        """Test getting next chapter"""
        next_chapter = ChapterService.get_next_chapter(self.approved_chapter)
        
        # Should skip pending chapter and return the next available published chapter
        # Since hidden chapter is not considered published, should return None
        self.assertIsNone(next_chapter)
    
    def test_get_previous_chapter(self):
        """Test getting previous chapter"""
        previous_chapter = ChapterService.get_previous_chapter(self.pending_chapter)
        
        self.assertEqual(previous_chapter, self.approved_chapter)
    
    def test_get_user_chapters(self):
        """Test getting chapters by user"""
        user_chapters = ChapterService.get_user_chapters(self.user, self.novel)
        
        # All chapters belong to this user's novel
        self.assertEqual(user_chapters.count(), 3)
        self.assertIn(self.approved_chapter, user_chapters)
        self.assertIn(self.pending_chapter, user_chapters)
        self.assertIn(self.hidden_chapter, user_chapters)
    
    def test_get_pending_chapters_for_review(self):
        """Test getting chapters pending review"""
        pending_chapters = ChapterService.get_pending_chapters_for_review()
        
        self.assertIn(self.pending_chapter, pending_chapters)
        self.assertNotIn(self.approved_chapter, pending_chapters)
        self.assertNotIn(self.hidden_chapter, pending_chapters)


class ChapterServiceStatisticsTests(ChapterServiceTestCase):
    """Test ChapterService statistics methods"""
    
    def setUp(self):
        super().setUp()
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1,
            view_count=100,
            word_count=500
        )
    
    @patch('novels.services.chapter_service.update_view_count')
    def test_increment_view_count(self, mock_update_view_count):
        """Test incrementing chapter view count"""
        ChapterService.increment_view_count(self.chapter.id)
        
        mock_update_view_count.assert_called_once_with(self.chapter.id)
    
    def test_get_chapter_statistics(self):
        """Test getting chapter statistics"""
        stats = ChapterService.get_chapter_statistics(self.chapter.id)
        
        self.assertIn('view_count', stats)
        self.assertIn('word_count', stats)
        self.assertIn('rating_average', stats)
        self.assertIn('rating_count', stats)
        self.assertIn('comment_count', stats)
        
        self.assertEqual(stats['view_count'], 100)
        self.assertEqual(stats['word_count'], 500)
    
    def test_calculate_reading_time(self):
        """Test calculating reading time"""
        reading_time = ChapterService.calculate_reading_time(self.chapter.id)
        
        # Assuming average reading speed of 200 words per minute
        # 500 words should take 2.5 minutes
        expected_time = 500 / 200
        self.assertEqual(reading_time, expected_time)


class ChapterServiceValidationTests(ChapterServiceTestCase):
    """Test ChapterService validation methods"""
    
    def test_validate_chapter_data_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_data = {
            'content': 'Test content'
            # Missing title and volume
        }
        
        with self.assertRaises(ValueError):
            ChapterService.validate_chapter_data(invalid_data)
    
    def test_validate_chapter_data_empty_title(self):
        """Test validation with empty title"""
        invalid_data = {
            'title': '',  # Empty title
            'content': 'Test content',
            'volume': self.volume
        }
        
        with self.assertRaises(ValueError):
            ChapterService.validate_chapter_data(invalid_data)
    
    def test_validate_chapter_data_empty_content(self):
        """Test validation with empty content"""
        invalid_data = {
            'title': 'Test Chapter',
            'content': '',  # Empty content
            'volume': self.volume
        }
        
        with self.assertRaises(ValueError):
            ChapterService.validate_chapter_data(invalid_data)
    
    def test_validate_chapter_data_invalid_position(self):
        """Test validation with invalid position"""
        invalid_data = {
            'title': 'Test Chapter',
            'content': 'Test content',
            'volume': self.volume,
            'position': 0  # Invalid position
        }
        
        with self.assertRaises(ValueError):
            ChapterService.validate_chapter_data(invalid_data)
    
    def test_validate_chapter_data_valid(self):
        """Test validation with valid data"""
        valid_data = {
            'title': 'Test Chapter',
            'content': 'Test content',
            'volume': self.volume
        }
        
        # Should not raise any exception
        ChapterService.validate_chapter_data(valid_data)
    
    def test_check_duplicate_chapter_position(self):
        """Test checking for duplicate chapter positions"""
        Chapter.objects.create(
            volume=self.volume,
            title="Existing Chapter",
            position=1
        )
        
        # Should raise exception for duplicate position
        with self.assertRaises(ValueError):
            ChapterService.check_duplicate_chapter_position(self.volume, 1)
        
        # Should not raise exception for unique position
        ChapterService.check_duplicate_chapter_position(self.volume, 2)


class ChapterServiceDeleteTests(ChapterServiceTestCase):
    """Test ChapterService deletion methods"""
    
    def setUp(self):
        super().setUp()
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=UserRole.ADMIN.value
        )
    
    def test_soft_delete_chapter_by_owner(self):
        """Test soft deleting chapter by owner"""
        deleted_chapter = ChapterService.soft_delete_chapter(
            self.chapter.id, 
            self.user
        )
        
        self.assertTrue(deleted_chapter.is_deleted)
        self.assertIsNotNone(deleted_chapter.deleted_at)
    
    def test_soft_delete_chapter_by_admin(self):
        """Test soft deleting chapter by admin"""
        deleted_chapter = ChapterService.soft_delete_chapter(
            self.chapter.id, 
            self.admin_user
        )
        
        self.assertTrue(deleted_chapter.is_deleted)
        self.assertIsNotNone(deleted_chapter.deleted_at)
    
    def test_soft_delete_chapter_permission_check(self):
        """Test soft delete permission checking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        with self.assertRaises(PermissionError):
            ChapterService.soft_delete_chapter(self.chapter.id, other_user)
    
    def test_restore_chapter(self):
        """Test restoring soft deleted chapter"""
        # First soft delete
        ChapterService.soft_delete_chapter(self.chapter.id, self.user)
        
        # Then restore
        restored_chapter = ChapterService.restore_chapter(
            self.chapter.id, 
            self.admin_user
        )
        
        self.assertFalse(restored_chapter.is_deleted)
        self.assertIsNone(restored_chapter.deleted_at)
    
    def test_restore_chapter_permission_check(self):
        """Test restore chapter permission checking"""
        # Soft delete first
        ChapterService.soft_delete_chapter(self.chapter.id, self.user)
        
        # User cannot restore
        with self.assertRaises(PermissionError):
            ChapterService.restore_chapter(self.chapter.id, self.user)


class ChapterServiceOrderingTests(ChapterServiceTestCase):
    """Test ChapterService ordering and reordering methods"""
    
    def setUp(self):
        super().setUp()
        # Create multiple chapters
        self.chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 1",
            position=1
        )
        
        self.chapter2 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 2",
            position=2
        )
        
        self.chapter3 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 3",
            position=3
        )
    
    def test_reorder_chapters(self):
        """Test reordering chapters"""
        new_order = {
            self.chapter1.id: 3,
            self.chapter2.id: 1,
            self.chapter3.id: 2
        }
        
        ChapterService.reorder_chapters(self.volume, new_order, self.user)
        
        # Refresh from database
        self.chapter1.refresh_from_db()
        self.chapter2.refresh_from_db()
        self.chapter3.refresh_from_db()
        
        self.assertEqual(self.chapter1.position, 3)
        self.assertEqual(self.chapter2.position, 1)
        self.assertEqual(self.chapter3.position, 2)
    
    def test_reorder_chapters_permission_check(self):
        """Test reordering permission checking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        new_order = {self.chapter1.id: 2, self.chapter2.id: 1}
        
        with self.assertRaises(PermissionError):
            ChapterService.reorder_chapters(self.volume, new_order, other_user)
    
    def test_insert_chapter_at_position(self):
        """Test inserting chapter at specific position"""
        chapter_data = {
            'title': 'Inserted Chapter',
            'content': 'Inserted content',
            'volume': self.volume,
            'position': 2  # Insert between existing chapters
        }
        
        with patch('novels.services.chapter_service.ChunkManager.create_chunks') as mock_create_chunks:
            mock_create_chunks.return_value = [Mock(content="Test", word_count=1)]
            
            new_chapter = ChapterService.create_chapter_at_position(
                chapter_data, 
                self.user
            )
        
        # Check new chapter position
        self.assertEqual(new_chapter.position, 2)
        
        # Check other chapters were reordered
        self.chapter2.refresh_from_db()
        self.chapter3.refresh_from_db()
        
        self.assertEqual(self.chapter2.position, 3)
        self.assertEqual(self.chapter3.position, 4)
