"""
Unit tests for Chapter Model functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from novels.models import Novel, Volume, Chapter, Author, Artist
from constants import ApprovalStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")


User = get_user_model()


class ChapterModelTestCase(TestCase):
    """Base test case for chapter model tests"""
    
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
            name="Test Volume 1",
            position=1
        )


class ChapterModelCreationTests(ChapterModelTestCase):
    """Test Chapter model creation and basic functionality"""
    
    def test_chapter_creation_minimal(self):
        """Test creating chapter with minimal required fields"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        self.assertEqual(chapter.title, "Test Chapter")
        self.assertEqual(chapter.volume, self.volume)
        self.assertEqual(chapter.position, 1)
        self.assertIsNotNone(chapter.slug)
        self.assertFalse(chapter.approved)
        self.assertFalse(chapter.is_hidden)
        self.assertEqual(chapter.word_count, 0)
        self.assertEqual(chapter.view_count, 0)
    
    def test_chapter_creation_with_all_fields(self):
        """Test creating chapter with all fields"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Complete Chapter",
            position=1,
            word_count=1000,
            view_count=500,
            approved=True,
            is_hidden=False,
            rejected_reason=None
        )
        
        self.assertEqual(chapter.title, "Complete Chapter")
        self.assertEqual(chapter.word_count, 1000)
        self.assertEqual(chapter.view_count, 500)
        self.assertTrue(chapter.approved)
        self.assertFalse(chapter.is_hidden)
    
    def test_chapter_str_representation(self):
        """Test chapter string representation"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        expected = f"{self.novel.name} - Test Chapter"
        self.assertEqual(str(chapter), expected)


class ChapterModelSlugTests(ChapterModelTestCase):
    """Test Chapter model slug generation"""
    
    def test_slug_generation_from_volume_and_title(self):
        """Test automatic slug generation"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter Title",
            position=1
        )
        
        # Should include volume and chapter information
        self.assertIsNotNone(chapter.slug)
        self.assertIn("test", chapter.slug.lower())
    
    def test_slug_uniqueness(self):
        """Test slug uniqueness across all chapters"""
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        # Create another volume
        volume2 = Volume.objects.create(
            novel=self.novel,
            name="Test Volume 2",
            position=2
        )
        
        chapter2 = Chapter.objects.create(
            volume=volume2,
            title="Test Chapter",  # Same title, different volume
            position=1
        )
        
        self.assertNotEqual(chapter1.slug, chapter2.slug)
    
    def test_slug_generation_special_characters(self):
        """Test slug generation with special characters"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Chapter: Special Characters!",
            position=1
        )
        
        # Should remove special characters
        self.assertNotIn(":", chapter.slug)
        self.assertNotIn("!", chapter.slug)
    
    def test_slug_generation_empty_title(self):
        """Test slug generation with empty title"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="   ",  # Whitespace only
            position=1
        )
        
        # Should generate default slug based on position
        self.assertIn("chuong", chapter.slug.lower())
        self.assertIn("1", chapter.slug)


class ChapterModelValidationTests(ChapterModelTestCase):
    """Test Chapter model validation"""
    
    def test_volume_required(self):
        """Test that volume is required"""
        # Chapter model's save method requires volume to generate slug
        # So we test this at validation level instead
        with self.assertRaises(ValidationError):
            chapter = Chapter(
                title="Test Chapter",
                position=1
            )
            chapter.full_clean()
    
    def test_title_required(self):
        """Test that title is required"""
        with self.assertRaises(ValidationError):
            chapter = Chapter(
                volume=self.volume,
                position=1
            )
            chapter.full_clean()
    
    def test_position_required(self):
        """Test that position is required"""
        with self.assertRaises(ValidationError):
            chapter = Chapter(
                volume=self.volume,
                title="Test Chapter"
            )
            chapter.full_clean()
    
    def test_unique_position_in_volume(self):
        """Test unique position constraint within volume"""
        Chapter.objects.create(
            volume=self.volume,
            title="First Chapter",
            position=1
        )
        
        # Try to create another chapter with same position in same volume
        with self.assertRaises(IntegrityError):
            Chapter.objects.create(
                volume=self.volume,
                title="Second Chapter",
                position=1  # Duplicate position
            )
    
    def test_different_positions_same_volume_allowed(self):
        """Test different positions in same volume are allowed"""
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="First Chapter",
            position=1
        )
        
        chapter2 = Chapter.objects.create(
            volume=self.volume,
            title="Second Chapter",
            position=2
        )
        
        self.assertEqual(chapter1.volume, chapter2.volume)
        self.assertNotEqual(chapter1.position, chapter2.position)
    
    def test_same_position_different_volumes_allowed(self):
        """Test same position in different volumes is allowed"""
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="First Chapter",
            position=1
        )
        
        # Create another volume
        volume2 = Volume.objects.create(
            novel=self.novel,
            name="Test Volume 2",
            position=2
        )
        
        chapter2 = Chapter.objects.create(
            volume=volume2,
            title="Another First Chapter",
            position=1  # Same position, different volume
        )
        
        self.assertNotEqual(chapter1.volume, chapter2.volume)
        self.assertEqual(chapter1.position, chapter2.position)


class ChapterModelRelationshipTests(ChapterModelTestCase):
    """Test Chapter model relationships"""
    
    def test_volume_relationship(self):
        """Test chapter-volume relationship"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        self.assertEqual(chapter.volume, self.volume)
        self.assertIn(chapter, self.volume.chapters.all())
    
    def test_novel_property(self):
        """Test chapter.novel property"""
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        self.assertEqual(chapter.novel, self.novel)
    
    def test_chunks_relationship(self):
        """Test chapter-chunks relationship"""
        from novels.models import Chunk
        
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        # Create test chunks
        chunk1 = Chunk.objects.create(
            chapter=chapter,
            content="First chunk content",
            position=1,
            word_count=3
        )
        
        chunk2 = Chunk.objects.create(
            chapter=chapter,
            content="Second chunk content",
            position=2,
            word_count=3
        )
        
        self.assertEqual(chapter.chunks.count(), 2)
        self.assertIn(chunk1, chapter.chunks.all())
        self.assertIn(chunk2, chapter.chunks.all())


class ChapterModelMethodTests(ChapterModelTestCase):
    """Test Chapter model custom methods"""
    
    def test_get_content_method(self):
        """Test get_content method combines chunks"""
        from novels.models import Chunk
        
        chapter = Chapter.objects.create(
            volume=self.volume,
            title="Test Chapter",
            position=1
        )
        
        # Create test chunks
        Chunk.objects.create(
            chapter=chapter,
            content="First chunk content",
            position=1,
            word_count=3
        )
        
        Chunk.objects.create(
            chapter=chapter,
            content="Second chunk content",
            position=2,
            word_count=3
        )
        
        content = chapter.get_content()
        self.assertIn("First chunk content", content)
        self.assertIn("Second chunk content", content)
    
    def test_get_next_chapter(self):
        """Test get_next_chapter method"""
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 1",
            position=1,
            approved=True,
            is_hidden=False
        )
        
        chapter2 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 2",
            position=2,
            approved=True,
            is_hidden=False
        )
        
        next_chapter = chapter1.get_next_chapter()
        self.assertEqual(next_chapter, chapter2)
    
    def test_get_previous_chapter(self):
        """Test get_previous_chapter method"""
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 1",
            position=1,
            approved=True,
            is_hidden=False
        )
        
        chapter2 = Chapter.objects.create(
            volume=self.volume,
            title="Chapter 2",
            position=2,
            approved=True,
            is_hidden=False
        )
        
        previous_chapter = chapter2.get_previous_chapter()
        self.assertEqual(previous_chapter, chapter1)
    
    def test_get_next_chapter_cross_volume(self):
        """Test get_next_chapter across volumes"""
        # Create chapter1 at end of volume 1
        chapter1 = Chapter.objects.create(
            volume=self.volume,
            title="Last Chapter Vol 1",
            position=2,  # Last chapter in volume 1
            approved=True,
            is_hidden=False
        )
        
        # Create second volume
        volume2 = Volume.objects.create(
            novel=self.novel,
            name="Volume 2",
            position=2
        )
        
        # Create first chapter in volume 2
        chapter2 = Chapter.objects.create(
            volume=volume2,
            title="First Chapter Vol 2",
            position=1,
            approved=True,
            is_hidden=False
        )
        
        # Current implementation looks for position__gt=self.position
        # across all volumes, so it won't find chapter2 (position 1) 
        # when looking from chapter1 (position 2)
        next_chapter = chapter1.get_next_chapter()
        self.assertEqual(next_chapter, chapter2)
        
        # To find a next chapter, we'd need a chapter with position > 2
        chapter3 = Chapter.objects.create(
            volume=volume2,
            title="Second Chapter Vol 2",
            position=3,  # position > 2
            approved=True,
            is_hidden=False
        )
        
        next_chapter = chapter2.get_next_chapter()
        self.assertEqual(next_chapter, chapter3)
