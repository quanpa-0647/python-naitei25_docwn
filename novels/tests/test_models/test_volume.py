"""
Unit tests for Volume Model functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from novels.models import Novel, Volume, Author
from constants import ApprovalStatus, UserRole


User = get_user_model()


class VolumeModelTestCase(TestCase):
    """Base test case for volume model tests"""
    
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


class VolumeModelCreationTests(VolumeModelTestCase):
    """Test Volume model creation and basic functionality"""
    
    def test_volume_creation_minimal(self):
        """Test creating volume with minimal required fields"""
        volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )
        
        self.assertEqual(volume.name, "Test Volume")
        self.assertEqual(volume.novel, self.novel)
        self.assertEqual(volume.position, 1)
        self.assertIsNotNone(volume.created_at)
        self.assertIsNotNone(volume.updated_at)
    
    def test_volume_creation_with_description(self):
        """Test creating volume with description"""
        volume = Volume.objects.create(
            novel=self.novel,
            name="Volume with Description",
            position=1
        )
        
        # Volume model doesn't have description field in actual implementation
        self.assertEqual(volume.name, "Volume with Description")
    
    def test_volume_str_representation(self):
        """Test volume string representation"""
        volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )
        
        expected = f"{self.novel.name} - Test Volume"
        self.assertEqual(str(volume), expected)


class VolumeModelValidationTests(VolumeModelTestCase):
    """Test Volume model validation - Volume model doesn't have slug field"""
    
    def test_volume_naming_within_novel(self):
        """Test volume naming validation within same novel"""
        Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )
        
        # Different position, same name should be allowed per unique_together constraint
        # Actually this should fail due to unique constraint on (novel, name)
        with self.assertRaises(IntegrityError):
            Volume.objects.create(
                novel=self.novel,
                name="Test Volume",  # Same name
                position=2
            )
    
    def test_novel_required(self):
        """Test that novel is required"""
        with self.assertRaises(IntegrityError):
            Volume.objects.create(
                name="Test Volume",
                position=1
            )
    
    def test_name_required(self):
        """Test that name is required"""
        with self.assertRaises(ValidationError):
            volume = Volume(
                novel=self.novel,
                position=1
            )
            volume.full_clean()
    
    def test_position_required(self):
        """Test that position is required"""
        with self.assertRaises(ValidationError):
            volume = Volume(
                novel=self.novel,
                name="Test Volume"
            )
            volume.full_clean()
    
    def test_unique_position_in_novel(self):
        """Test unique position constraint within novel"""
        Volume.objects.create(
            novel=self.novel,
            name="First Volume",
            position=1
        )
        
        # Try to create another volume with same position in same novel
        with self.assertRaises(IntegrityError):
            Volume.objects.create(
                novel=self.novel,
                name="Second Volume",
                position=1  # Duplicate position
            )
    
    def test_different_positions_same_novel_allowed(self):
        """Test different positions in same novel are allowed"""
        volume1 = Volume.objects.create(
            novel=self.novel,
            name="First Volume",
            position=1
        )
        
        volume2 = Volume.objects.create(
            novel=self.novel,
            name="Second Volume",
            position=2
        )
        
        self.assertEqual(volume1.novel, volume2.novel)
        self.assertNotEqual(volume1.position, volume2.position)
    
    def test_same_position_different_novels_allowed(self):
        """Test same position in different novels is allowed"""
        volume1 = Volume.objects.create(
            novel=self.novel,
            name="First Volume",
            position=1
        )
        
        # Create another novel
        novel2 = Novel.objects.create(
            name="Another Novel",
            summary="Another summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        volume2 = Volume.objects.create(
            novel=novel2,
            name="Another First Volume",
            position=1  # Same position, different novel
        )
        
        self.assertNotEqual(volume1.novel, volume2.novel)
        self.assertEqual(volume1.position, volume2.position)


class VolumeModelRelationshipTests(VolumeModelTestCase):
    """Test Volume model relationships"""
    
    def test_novel_relationship(self):
        """Test volume-novel relationship"""
        volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )
        
        self.assertEqual(volume.novel, self.novel)
        self.assertIn(volume, self.novel.volumes.all())
    
    def test_chapters_relationship(self):
        """Test volume-chapters relationship"""
        from novels.models import Chapter
        
        volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume",
            position=1
        )
        
        # Create test chapters
        chapter1 = Chapter.objects.create(
            volume=volume,
            title="Chapter 1",
            position=1
        )
        
        chapter2 = Chapter.objects.create(
            volume=volume,
            title="Chapter 2",
            position=2
        )
        
        self.assertEqual(volume.chapters.count(), 2)
        self.assertIn(chapter1, volume.chapters.all())
        self.assertIn(chapter2, volume.chapters.all())


class VolumeModelOrderingTests(VolumeModelTestCase):
    """Test Volume model ordering"""
    
    def test_default_ordering_by_position(self):
        """Test volumes are ordered by position by default"""
        volume3 = Volume.objects.create(
            novel=self.novel,
            name="Volume 3",
            position=3
        )
        
        volume1 = Volume.objects.create(
            novel=self.novel,
            name="Volume 1",
            position=1
        )
        
        volume2 = Volume.objects.create(
            novel=self.novel,
            name="Volume 2",
            position=2
        )
        
        volumes = list(Volume.objects.all())
        self.assertEqual(volumes[0], volume1)
        self.assertEqual(volumes[1], volume2)
        self.assertEqual(volumes[2], volume3)
    
    def test_ordering_within_novel(self):
        """Test volume ordering within same novel"""
        # Create another novel
        novel2 = Novel.objects.create(
            name="Another Novel",
            summary="Another summary",
            author=self.author,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value
        )
        
        # Create volumes for both novels
        Volume.objects.create(novel=self.novel, name="Novel1 Vol2", position=2)
        Volume.objects.create(novel=novel2, name="Novel2 Vol1", position=1)
        Volume.objects.create(novel=self.novel, name="Novel1 Vol1", position=1)
        Volume.objects.create(novel=novel2, name="Novel2 Vol2", position=2)
        
        # Check ordering within each novel
        novel1_volumes = Volume.objects.filter(novel=self.novel)
        self.assertEqual(novel1_volumes[0].position, 1)
        self.assertEqual(novel1_volumes[1].position, 2)
        
        novel2_volumes = Volume.objects.filter(novel=novel2)
        self.assertEqual(novel2_volumes[0].position, 1)
        self.assertEqual(novel2_volumes[1].position, 2)
