"""
Unit tests for Novel Model functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from novels.models import Novel, Author, Artist, Tag
from constants import ApprovalStatus, ProgressStatus, UserRole


User = get_user_model()


class NovelModelTestCase(TestCase):
    """Base test case for novel model tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create test author and artist
        self.author = Author.objects.create(
            name="Test Author",
            description="Test author description"
        )
        
        self.artist = Artist.objects.create(
            name="Test Artist",
            description="Test artist description"
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name="Romance", slug="romance")
        self.tag2 = Tag.objects.create(name="Fantasy", slug="fantasy")


class NovelModelCreationTests(NovelModelTestCase):
    """Test Novel model creation and basic functionality"""
    
    def test_novel_creation_minimal(self):
        """Test creating novel with minimal required fields"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            created_by=self.user
        )
        
        self.assertEqual(novel.name, "Test Novel")
        self.assertEqual(novel.summary, "Test summary")
        self.assertEqual(novel.created_by, self.user)
        self.assertIsNotNone(novel.slug)
        self.assertEqual(novel.approval_status, ApprovalStatus.DRAFT.value)
        self.assertEqual(novel.progress_status, ProgressStatus.ONGOING.value)
    
    def test_novel_creation_with_all_fields(self):
        """Test creating novel with all fields"""
        novel = Novel.objects.create(
            name="Complete Novel",
            summary="Complete summary",
            author=self.author,
            artist=self.artist,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status=ProgressStatus.COMPLETED.value,
            is_anonymous=True,
            other_names="Alternative Title",
            image_url="http://example.com/image.jpg",
            view_count=100,
            favorite_count=50,
            rating_avg=4.5,
            word_count=10000
        )
        
        self.assertEqual(novel.name, "Complete Novel")
        self.assertEqual(novel.author, self.author)
        self.assertEqual(novel.artist, self.artist)
        self.assertEqual(novel.approval_status, ApprovalStatus.APPROVED.value)
        self.assertEqual(novel.progress_status, ProgressStatus.COMPLETED.value)
        self.assertTrue(novel.is_anonymous)
        self.assertEqual(novel.view_count, 100)
        self.assertEqual(novel.rating_avg, 4.5)
    
    def test_novel_str_representation(self):
        """Test novel string representation"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            created_by=self.user
        )
        
        self.assertEqual(str(novel), "Test Novel")


class NovelModelSlugTests(NovelModelTestCase):
    """Test Novel model slug generation"""
    
    def test_slug_generation_from_name(self):
        """Test automatic slug generation from name"""
        novel = Novel.objects.create(
            name="Test Novel with Spaces",
            summary="Test summary",
            created_by=self.user
        )
        
        self.assertEqual(novel.slug, "test-novel-with-spaces")
    
    def test_slug_generation_unique(self):
        """Test slug uniqueness when names are similar"""
        novel1 = Novel.objects.create(
            name="Test Novel",
            summary="First summary",
            created_by=self.user
        )
        
        novel2 = Novel.objects.create(
            name="Test Novel",
            summary="Second summary",
            created_by=self.user
        )
        
        self.assertNotEqual(novel1.slug, novel2.slug)
        self.assertTrue(novel2.slug.startswith("test-novel"))
    
    def test_slug_generation_special_characters(self):
        """Test slug generation with special characters"""
        novel = Novel.objects.create(
            name="Test Novel: Special Characters!",
            summary="Test summary",
            created_by=self.user
        )
        
        # Should remove special characters
        self.assertNotIn(":", novel.slug)
        self.assertNotIn("!", novel.slug)
    
    def test_slug_generation_empty_name(self):
        """Test slug generation with empty or whitespace name"""
        novel = Novel.objects.create(
            name="   ",  # Whitespace only
            summary="Test summary",
            created_by=self.user
        )
        
        # Should generate default name and slug
        self.assertEqual(novel.name, "Untitled Novel")
        self.assertEqual(novel.slug, "untitled-novel")
    
    def test_slug_generation_non_latin_characters(self):
        """Test slug generation with non-Latin characters"""
        novel = Novel.objects.create(
            name="Tiểu Thuyết Tiếng Việt",
            summary="Test summary",
            created_by=self.user
        )
        
        # Should handle Vietnamese characters
        self.assertIsNotNone(novel.slug)
        self.assertNotEqual(novel.slug, "")


class NovelModelValidationTests(NovelModelTestCase):
    """Test Novel model validation"""
    
    def test_name_required(self):
        """Test that name is required"""
        with self.assertRaises(ValidationError):
            novel = Novel(
                summary="Test summary",
                created_by=self.user
            )
            novel.full_clean()
    
    def test_summary_required(self):
        """Test that summary is required"""
        with self.assertRaises(ValidationError):
            novel = Novel(
                name="Test Novel",
                created_by=self.user
            )
            novel.full_clean()
    
    def test_rating_validation(self):
        """Test rating field validation"""
        # Create a complete novel object that won't fail validation
        novel = Novel.objects.create(
            name="Rating Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user,
            rating_avg=4.5
        )
        
        # Test valid rating - should save without issues
        self.assertEqual(novel.rating_avg, 4.5)
        
        # Test that the novel was created successfully
        self.assertIsNotNone(novel.id)
    
    def test_unique_slug_constraint(self):
        """Test slug uniqueness constraint"""
        novel1 = Novel.objects.create(
            name="Test Novel",
            summary="First summary",
            created_by=self.user
        )
        
        # Try to create another novel with same slug manually
        with self.assertRaises(IntegrityError):
            Novel.objects.create(
                name="Different Name",
                slug=novel1.slug,  # Same slug
                summary="Second summary",
                created_by=self.user
            )


class NovelModelRelationshipTests(NovelModelTestCase):
    """Test Novel model relationships"""
    
    def test_author_relationship(self):
        """Test novel-author relationship"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            author=self.author,
            created_by=self.user
        )
        
        self.assertEqual(novel.author, self.author)
        self.assertIn(novel, self.author.novels.all())
    
    def test_artist_relationship(self):
        """Test novel-artist relationship"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            artist=self.artist,
            created_by=self.user
        )
        
        self.assertEqual(novel.artist, self.artist)
        self.assertIn(novel, self.artist.novels.all())
    
    def test_tags_relationship(self):
        """Test novel-tags many-to-many relationship"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            created_by=self.user
        )
        
        novel.tags.set([self.tag1, self.tag2])
        
        self.assertEqual(novel.tags.count(), 2)
        self.assertIn(self.tag1, novel.tags.all())
        self.assertIn(self.tag2, novel.tags.all())
        self.assertIn(novel, self.tag1.novels.all())
    
    def test_created_by_relationship(self):
        """Test novel-user relationship"""
        novel = Novel.objects.create(
            name="Test Novel",
            summary="Test summary",
            created_by=self.user
        )
        
        self.assertEqual(novel.created_by, self.user)
        self.assertIn(novel, self.user.created_novels.all())


class NovelModelMethodTests(NovelModelTestCase):
    """Test Novel model custom methods"""
    
    def test_save_method_default_values(self):
        """Test save method sets default values correctly"""
        novel = Novel(
            name="",  # Empty name
            summary="",  # Empty summary
            created_by=self.user
        )
        novel.save()
        
        # Should set default values
        self.assertEqual(novel.name, "Untitled Novel")
        self.assertEqual(novel.summary, "No summary available")
        self.assertIsNotNone(novel.slug)
    
    def test_save_method_preserves_existing_values(self):
        """Test save method doesn't override existing values"""
        novel = Novel(
            name="Custom Novel",
            summary="Custom summary",
            created_by=self.user
        )
        novel.save()
        
        # Should preserve custom values
        self.assertEqual(novel.name, "Custom Novel")
        self.assertEqual(novel.summary, "Custom summary")
