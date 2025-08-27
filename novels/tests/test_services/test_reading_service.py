"""
Unit tests for ReadingService functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from novels.services.reading_service import ReadingService
from novels.models import Novel, Volume, Chapter, ReadingHistory, Author
from constants import ApprovalStatus, ProgressStatus, UserRole, PROGRESS_DEFAULT
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class ReadingServiceTestCase(TestCase):
    """Base test case for ReadingService tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        # For anonymous user testing, use Django's AnonymousUser
        from django.contrib.auth.models import AnonymousUser
        self.anonymous_user = AnonymousUser()
        
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
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.ONGOING.value
        )
        
        # Create test volume
        self.volume = Volume.objects.create(
            novel=self.novel,
            name="Volume 1",
            position=1
        )
        
        # Create test chapter
        self.chapter = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 1",
            position=1
        )


class ReadingServiceGetOrCreateHistoryTests(ReadingServiceTestCase):
    """Test get_or_create_reading_history method"""
    
    def test_get_or_create_for_authenticated_user_new_history(self):
        """Test creating new reading history for authenticated user"""
        reading_history = ReadingService.get_or_create_reading_history(
            self.user, 
            self.chapter
        )
        
        self.assertIsNotNone(reading_history)
        self.assertEqual(reading_history.user, self.user)
        self.assertEqual(reading_history.chapter, self.chapter)
        self.assertEqual(reading_history.novel, self.novel)
        self.assertEqual(reading_history.reading_progress, PROGRESS_DEFAULT)
        
        # Verify it was saved to database
        self.assertTrue(ReadingHistory.objects.filter(
            user=self.user,
            chapter=self.chapter
        ).exists())
    
    def test_get_or_create_for_authenticated_user_existing_history(self):
        """Test getting existing reading history for authenticated user"""
        # Create existing reading history
        existing_history = ReadingHistory.objects.create(
            user=self.user,
            chapter=self.chapter,
            novel=self.novel,
            reading_progress=50
        )
        
        reading_history = ReadingService.get_or_create_reading_history(
            self.user, 
            self.chapter
        )
        
        # Should return the existing history
        self.assertEqual(reading_history.id, existing_history.id)
        self.assertEqual(reading_history.reading_progress, 50)
        
        # Should not create a new record
        self.assertEqual(ReadingHistory.objects.filter(
            user=self.user,
            chapter=self.chapter
        ).count(), 1)
    
    def test_get_or_create_for_anonymous_user(self):
        """Test that anonymous users return None"""
        reading_history = ReadingService.get_or_create_reading_history(
            self.anonymous_user, 
            self.chapter
        )
        
        self.assertIsNone(reading_history)
        
        # Verify no record was created
        self.assertFalse(ReadingHistory.objects.filter(
            chapter=self.chapter
        ).exists())
    
    def test_get_or_create_for_unauthenticated_user(self):
        """Test that unauthenticated users return None"""
        # Use anonymous user
        reading_history = ReadingService.get_or_create_reading_history(
            self.anonymous_user, self.chapter
        )
        self.assertIsNone(reading_history)


class ReadingServiceSaveProgressTests(ReadingServiceTestCase):
    """Test save_reading_progress method"""
    
    def test_save_progress_new_history(self):
        """Test saving progress creates new reading history"""
        chunk_position = 5
        reading_progress = 75
        
        reading_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            chunk_position,
            reading_progress
        )
        
        self.assertIsNotNone(reading_history)
        self.assertEqual(reading_history.user, self.user)
        self.assertEqual(reading_history.chapter, self.chapter)
        self.assertEqual(reading_history.novel, self.novel)
        self.assertEqual(reading_history.reading_progress, reading_progress)
        
        # Verify it was saved to database
        saved_history = ReadingHistory.objects.get(
            user=self.user,
            chapter=self.chapter
        )
        self.assertEqual(saved_history.reading_progress, reading_progress)
    
    def test_save_progress_existing_history(self):
        """Test saving progress updates existing reading history"""
        # Create existing reading history
        existing_history = ReadingHistory.objects.create(
            user=self.user,
            chapter=self.chapter,
            novel=self.novel,
            reading_progress=25
        )
        
        new_chunk_position = 8
        new_reading_progress = 90
        
        reading_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            new_chunk_position,
            new_reading_progress
        )
        
        # Should return the same instance (updated)
        self.assertEqual(reading_history.id, existing_history.id)
        self.assertEqual(reading_history.reading_progress, new_reading_progress)
        
        # Should not create a new record
        self.assertEqual(ReadingHistory.objects.filter(
            user=self.user,
            chapter=self.chapter
        ).count(), 1)
        
        # Verify changes were saved
        updated_history = ReadingHistory.objects.get(id=existing_history.id)
        self.assertEqual(updated_history.reading_progress, new_reading_progress)
    
    def test_save_progress_invalid_chapter_id(self):
        """Test saving progress with invalid chapter ID raises 404"""
        invalid_chapter_id = 9999
        
        with self.assertRaises(Exception):  # get_object_or_404 raises Http404
            ReadingService.save_reading_progress(
                self.user,
                invalid_chapter_id,
                5,
                75
            )
    
    def test_save_progress_zero_values(self):
        """Test saving progress with zero values"""
        reading_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            0,  # Zero chunk position
            0   # Zero progress
        )
        
        self.assertEqual(reading_history.reading_progress, 0)
        self.assertEqual(reading_history.reading_progress, 0)
    
    def test_save_progress_maximum_values(self):
        """Test saving progress with maximum values"""
        reading_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            999,  # High chunk position
            100   # 100% progress
        )
        
        self.assertEqual(reading_history.reading_progress, 100)
        self.assertEqual(reading_history.reading_progress, 100)


class ReadingServiceIntegrationTests(ReadingServiceTestCase):
    """Test integration scenarios"""
    
    def test_multiple_chapters_same_novel(self):
        """Test reading progress across multiple chapters of same novel"""
        # Create second chapter
        chapter2 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 2",
            position=2
        )
        
        # Save progress for first chapter
        history1 = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            5,
            100  # Completed
        )
        
        # Save progress for second chapter
        history2 = ReadingService.save_reading_progress(
            self.user,
            chapter2.id,
            3,
            50
        )
        
        # Should have separate histories for each chapter
        self.assertNotEqual(history1.id, history2.id)
        self.assertEqual(history1.chapter, self.chapter)
        self.assertEqual(history2.chapter, chapter2)
        self.assertEqual(history1.novel, history2.novel)  # Same novel
        
        # Verify database state
        self.assertEqual(ReadingHistory.objects.filter(
            user=self.user,
            novel=self.novel
        ).count(), 2)
    
    def test_multiple_users_same_chapter(self):
        """Test reading progress for multiple users on same chapter"""
        # Create second user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Save progress for first user
        history1 = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            5,
            75
        )
        
        # Save progress for second user
        history2 = ReadingService.save_reading_progress(
            user2,
            self.chapter.id,
            3,
            50
        )
        
        # Should have separate histories for each user
        self.assertNotEqual(history1.id, history2.id)
        self.assertEqual(history1.user, self.user)
        self.assertEqual(history2.user, user2)
        self.assertEqual(history1.chapter, history2.chapter)  # Same chapter
        
        # Verify database state
        self.assertEqual(ReadingHistory.objects.filter(
            chapter=self.chapter
        ).count(), 2)
    
    def test_get_or_create_then_save_progress(self):
        """Test workflow of getting history then saving progress"""
        # First get or create reading history
        initial_history = ReadingService.get_or_create_reading_history(
            self.user,
            self.chapter
        )
        
        self.assertEqual(initial_history.reading_progress, PROGRESS_DEFAULT)
        self.assertEqual(initial_history.reading_progress, PROGRESS_DEFAULT)
        
        # Then save progress
        updated_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            7,
            85
        )
        
        # Should be the same instance, now updated
        self.assertEqual(initial_history.id, updated_history.id)
        self.assertEqual(updated_history.reading_progress, 85)


class ReadingServiceErrorHandlingTests(ReadingServiceTestCase):
    """Test error handling and edge cases"""
    
    def test_save_progress_with_none_user(self):
        """Test saving progress with None user"""
        # Should return None since we check user authentication
        reading_history = ReadingService.save_reading_progress(
            None,
            self.chapter.id,
            5,
            75
        )
        
        self.assertIsNone(reading_history)
    
    def test_get_or_create_with_none_user(self):
        """Test get_or_create with None user"""
        # This should handle gracefully since we check is_authenticated
        reading_history = ReadingService.get_or_create_reading_history(
            None,
            self.chapter
        )
        
        # Should return None since None doesn't have is_authenticated
        self.assertIsNone(reading_history)
    
    def test_get_or_create_with_none_chapter(self):
        """Test get_or_create with None chapter"""
        with self.assertRaises(Exception):
            ReadingService.get_or_create_reading_history(
                self.user,
                None
            )
    
    def test_save_progress_negative_values(self):
        """Test saving progress with negative values"""
        reading_history = ReadingService.save_reading_progress(
            self.user,
            self.chapter.id,
            -1,   # Negative chunk position
            -10   # Negative progress
        )
        
        # Service doesn't validate, just saves the values
        # Negative values should still be saved (service doesn't validate)
        self.assertEqual(reading_history.reading_progress, -10)
