"""
Unit tests for Chapter Form functionality
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unittest.mock import patch, Mock

from novels.models import Novel, Volume, Chapter, Author, Artist, Tag
from novels.forms import ChapterForm
from constants import ApprovalStatus, UserRole, MAX_CHUNK_SIZE
import warnings

warnings.filterwarnings("ignore", message="No directory at:")


User = get_user_model()


class ChapterFormTestCase(TestCase):
    """Base test case for chapter form tests"""
    
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
        
        # Create test novel
        self.novel = Novel.objects.create(
            name="Test Novel",
            slug="test-novel",
            summary="A test novel for testing",
            author=self.author,
            artist=self.artist,
            created_by=self.user,
            approval_status=ApprovalStatus.APPROVED.value,
            progress_status='o'
        )
        self.novel.tags.set([self.tag1, self.tag2])
        
        # Create test volume
        self.volume = Volume.objects.create(
            novel=self.novel,
            name="Test Volume 1",
            position=1
        )
        
        # Create existing chapter
        self.existing_chapter = Chapter.objects.create(
            volume=self.volume,
            title="Existing Chapter",
            slug="test-volume-1-existing-chapter",
            position=1,
            word_count=100,
            approved=True
        )


class ChapterFormInitializationTests(ChapterFormTestCase):
    """Test ChapterForm initialization"""
    
    def test_form_init_with_novel(self):
        """Test form initialization with novel"""
        form = ChapterForm(novel=self.novel)
        
        # Check volume choices are populated
        volume_choices = form.fields['volume_choice'].choices
        self.assertIn(('', '-- Chọn Volume --'), volume_choices)
        self.assertIn((self.volume.id, self.volume.name), volume_choices)
        self.assertIn(('new', 'Tạo Volume mới'), volume_choices)
    
    def test_form_init_without_novel(self):
        """Test form initialization without novel"""
        form = ChapterForm()
        
        # Check default volume choices
        volume_choices = form.fields['volume_choice'].choices
        self.assertEqual(len(volume_choices), 0)


class ChapterFormValidationTests(ChapterFormTestCase):
    """Test ChapterForm validation logic"""
    
    def test_valid_form_with_existing_volume(self):
        """Test valid form submission with existing volume"""
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': str(self.volume.id),
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['title'], 'New Chapter Title')
        self.assertEqual(form.cleaned_data['volume_choice'], str(self.volume.id))
    
    def test_valid_form_with_new_volume(self):
        """Test valid form submission with new volume"""
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': 'new',
            'new_volume_name': 'Brand New Volume',
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['new_volume_name'], 'Brand New Volume')
    
    def test_form_missing_title(self):
        """Test form validation with missing title"""
        form_data = {
            'volume_choice': str(self.volume.id),
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_missing_content(self):
        """Test form validation with missing content"""
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': str(self.volume.id)
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_form_missing_volume_choice(self):
        """Test form validation with missing volume choice"""
        form_data = {
            'title': 'New Chapter Title',
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_new_volume_without_name(self):
        """Test form validation when choosing new volume without providing name"""
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': 'new',
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_duplicate_volume_name(self):
        """Test form validation with duplicate volume name"""
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': 'new',
            'new_volume_name': self.volume.name,  # Duplicate name
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_duplicate_chapter_title_in_volume(self):
        """Test form validation with duplicate chapter title in same volume"""
        # First create an existing chapter with the title we'll try to duplicate
        Chapter.objects.create(
            volume=self.volume,
            title="Duplicate Title",
            position=2
        )
        
        form_data = {
            'title': 'Duplicate Title',  # Same title as existing chapter
            'volume_choice': str(self.volume.id),
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Tiêu đề chapter đã tồn tại trong volume này', str(form.errors))
    
    def test_clean_title_whitespace(self):
        """Test title cleaning removes whitespace"""
        form_data = {
            'title': '  New Chapter Title  ',
            'volume_choice': str(self.volume.id),
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'New Chapter Title')


class ChapterFormSaveTests(ChapterFormTestCase):
    """Test ChapterForm save functionality"""
    
    @patch('novels.utils.ChunkManager.create_html_chunks_for_chapter')
    def test_form_save_with_existing_volume(self, mock_create_chunks):
        """Test form save with existing volume"""
        mock_create_chunks.return_value = 2
        
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': str(self.volume.id),
            'content': '<p>This is the chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertTrue(form.is_valid())
        chapter = form.save()
        expected_position = self.volume.chapters.count()
        
        # Check chapter was created correctly
        self.assertEqual(chapter.title, 'New Chapter Title')
        self.assertEqual(chapter.volume, self.volume)
        self.assertEqual(chapter.position, expected_position) # First chapter since volume was empty
        self.assertFalse(chapter.approved)
        
        # Check chunks were created
        mock_create_chunks.assert_called_once()
    
    @patch('novels.utils.ChunkManager.create_html_chunks_for_chapter')
    def test_form_save_with_new_volume(self, mock_create_chunks):
        """Test form save with new volume"""
        mock_create_chunks.return_value = 3
        
        form_data = {
            'title': 'New Chapter Title',
            'volume_choice': 'new',
            'new_volume_name': 'Brand New Volume',
            'content': '<p>This is a longer chapter content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertTrue(form.is_valid())
        chapter = form.save()
        
        # Check new volume was created
        new_volume = Volume.objects.get(name='Brand New Volume')
        self.assertEqual(new_volume.novel, self.novel)
        self.assertEqual(new_volume.position, 2)
        
        # Check chapter was created correctly
        self.assertEqual(chapter.title, 'New Chapter Title')
        self.assertEqual(chapter.volume, new_volume)
        self.assertEqual(chapter.position, 1)
        
        # Check chunks were created
        mock_create_chunks.assert_called_once()
    
    def test_save_without_novel_raises_error(self):
        """Test that save() raises ValueError when novel is None"""
        form_data = {
            'title': 'Test Chapter',
            'volume_choice': 'new',
            'new_volume_name': 'New Volume',
            'content': '<p>Content</p>'
        }
        form = ChapterForm(data=form_data)  # No novel provided
        
        # Form should be invalid because volume choices are empty without novel
        self.assertFalse(form.is_valid())
        # The error should be about volume choice validation
        self.assertIn('volume_choice', form.errors)


class ChapterFormEdgeCaseTests(ChapterFormTestCase):
    """Test edge cases and boundary conditions"""
    
    def test_volume_position_calculation(self):
        """Test volume position calculation when creating new volume"""
        # Create additional volumes
        Volume.objects.create(novel=self.novel, name="Volume 2", position=2)
        Volume.objects.create(novel=self.novel, name="Volume 3", position=3)
        
        form_data = {
            'title': 'Test Chapter',
            'volume_choice': 'new',
            'new_volume_name': 'Volume 4',
            'content': '<p>Content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        with patch('novels.utils.ChunkManager.create_html_chunks_for_chapter'):
            chapter = form.save()
        
        # Check that new volume has correct position
        new_volume = Volume.objects.get(name='Volume 4')
        self.assertEqual(new_volume.position, 4)
    
    def test_chapter_position_calculation(self):
        """Test chapter position calculation within volume"""
        # The volume already has one chapter from setUp (self.existing_chapter at position 1)
        # Add more chapters to existing volume
        Chapter.objects.create(
            volume=self.volume, title="Chapter 2", 
            position=2
        )
        Chapter.objects.create(
            volume=self.volume, title="Chapter 3", 
            position=3
        )
        
        form_data = {
            'title': 'Chapter 4',
            'volume_choice': str(self.volume.id),
            'content': '<p>Content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        with patch('novels.utils.ChunkManager.create_html_chunks_for_chapter'):
            chapter = form.save()
        
        # Should be position 4 (after 3 existing chapters)
        self.assertEqual(chapter.position, 4)
    
    def test_invalid_volume_id_handling(self):
        """Test handling of invalid volume ID"""
        form_data = {
            'title': 'Test Chapter',
            'volume_choice': '99999',  # Non-existent volume ID
            'content': '<p>Content</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Select a valid choice', str(form.errors))
    
    @patch('novels.utils.ChunkManager.create_html_chunks_for_chapter')
    def test_html_chunker_integration(self, mock_chunk):
        """Test HTML chunker integration in save method"""
        form_data = {
            'title': 'HTML Test Chapter',
            'volume_choice': str(self.volume.id),
            'content': '<h1>Title</h1><p>Paragraph 1</p><p>Paragraph 2</p>'
        }
        form = ChapterForm(novel=self.novel, data=form_data)
        
        with patch('novels.forms.chapter_form.HtmlChunker') as mock_chunker_class:
            mock_chunker_instance = Mock()
            mock_chunker_class.return_value = mock_chunker_instance
            mock_chunk.return_value = 3
            
            chapter = form.save()
            
            # Verify HTML chunker was created with correct parameters
            mock_chunker_class.assert_called_once_with(max_chunk_size=MAX_CHUNK_SIZE)
            
            # Verify chunk creation was called with HTML chunker
            mock_chunk.assert_called_once_with(
                chapter=chapter,
                content=form_data['content'],
                chunker=mock_chunker_instance
            )
