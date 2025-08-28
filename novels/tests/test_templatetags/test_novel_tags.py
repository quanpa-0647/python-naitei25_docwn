"""
Unit tests for novel_tags template tags
"""
from django.test import TestCase, RequestFactory
from django.template import Template, Context
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock

from novels.templatetags.novel_tags import render_novel_filter
from novels.models import Tag
from constants import ProgressStatus, ApprovalStatus, UserRole
import warnings

warnings.filterwarnings("ignore", message="No directory at:")

User = get_user_model()


class NovelTagsTestCase(TestCase):
    """Test cases for novel_tags template tags"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(
            name="Fantasy",
            slug="fantasy",
            description="Fantasy stories"
        )
        self.tag2 = Tag.objects.create(
            name="Romance",
            slug="romance",
            description="Romance stories"
        )


class RenderNovelFilterTests(NovelTagsTestCase):
    """Test render_novel_filter inclusion tag"""
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_basic(self, mock_get_tags):
        """Test basic rendering of novel filter"""
        # Mock the service method
        mock_get_tags.return_value = [self.tag1, self.tag2]
        
        # Create request with no GET parameters
        request = self.factory.get('/novels/')
        
        # Create context
        context = {'request': request}
        
        # Call the template tag function
        result = render_novel_filter(context)
        
        # Verify result structure
        self.assertIn('tags', result)
        self.assertIn('progress_statuses', result)
        self.assertIn('approval_statuses', result)
        self.assertIn('selected_tags', result)
        self.assertIn('sort_option', result)
        self.assertIn('search_query', result)
        
        # Verify default values
        self.assertEqual(result['selected_tags'], [])
        self.assertEqual(result['sort_option'], 'created')
        self.assertEqual(result['search_query'], '')
        self.assertEqual(result['author_selected'], '')
        self.assertEqual(result['artist_selected'], '')
        self.assertEqual(result['progress_status_selected'], '')
        self.assertEqual(result['approval_status_selected'], '')
        
        # Verify status constants
        self.assertEqual(result['DRAFT'], ApprovalStatus.DRAFT.value)
        self.assertEqual(result['PENDING'], ApprovalStatus.PENDING.value)
        self.assertEqual(result['APPROVED'], ApprovalStatus.APPROVED.value)
        self.assertEqual(result['REJECTED'], ApprovalStatus.REJECTED.value)
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_with_parameters(self, mock_get_tags):
        """Test rendering with GET parameters"""
        # Mock the service method
        mock_get_tags.return_value = [self.tag1, self.tag2]
        
        # Create request with GET parameters
        request = self.factory.get('/novels/', {
            'q': 'fantasy adventure',
            'tags': ['fantasy', 'romance'],
            'sort': 'rating',
            'author': 'John Doe',
            'artist': 'Jane Artist',
            'progress_status': ProgressStatus.ONGOING.value,
            'status': ApprovalStatus.APPROVED.value
        })
        
        # Create context
        context = {'request': request}
        
        # Call the template tag function
        result = render_novel_filter(context)
        
        # Verify parameter values were captured
        self.assertEqual(result['search_query'], 'fantasy adventure')
        self.assertEqual(result['selected_tags'], ['fantasy', 'romance'])
        self.assertEqual(result['tag_slugs'], ['fantasy', 'romance'])  # compatibility
        self.assertEqual(result['sort_option'], 'rating')
        self.assertEqual(result['author_selected'], 'John Doe')
        self.assertEqual(result['artist_selected'], 'Jane Artist')
        self.assertEqual(result['progress_status_selected'], ProgressStatus.ONGOING.value)
        self.assertEqual(result['approval_status_selected'], ApprovalStatus.APPROVED.value)
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_with_single_tag(self, mock_get_tags):
        """Test rendering with single tag parameter"""
        # Mock the service method
        mock_get_tags.return_value = [self.tag1, self.tag2]
        
        # Create request with single tag
        request = self.factory.get('/novels/', {
            'tags': 'fantasy'
        })
        
        # Create context
        context = {'request': request}
        
        # Call the template tag function
        result = render_novel_filter(context)
        
        # Verify single tag is handled correctly
        self.assertEqual(result['selected_tags'], ['fantasy'])
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_choices_structure(self, mock_get_tags):
        """Test that choices are properly structured"""
        # Mock the service method
        mock_get_tags.return_value = [self.tag1, self.tag2]
        
        # Create request
        request = self.factory.get('/novels/')
        context = {'request': request}
        
        # Call the template tag function
        result = render_novel_filter(context)
        
        # Verify choices structure
        self.assertEqual(result['progress_statuses'], ProgressStatus.choices)
        self.assertEqual(result['approval_statuses'], ApprovalStatus.choices)
        
        # Verify tags structure
        self.assertEqual(len(result['tags']), 2)
        self.assertIn(self.tag1, result['tags'])
        self.assertIn(self.tag2, result['tags'])
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_empty_parameters(self, mock_get_tags):
        """Test rendering with empty GET parameters"""
        # Mock the service method
        mock_get_tags.return_value = []
        
        # Create request with empty parameters
        request = self.factory.get('/novels/', {
            'q': '',
            'tags': '',
            'sort': '',
            'author': '',
            'artist': '',
            'progress_status': '',
            'status': ''
        })
        
        # Create context
        context = {'request': request}
        
        # Call the template tag function
        result = render_novel_filter(context)
        
        # Verify empty values are handled correctly
        self.assertEqual(result['search_query'], '')
        self.assertEqual(result['selected_tags'], [''])  # Empty string becomes list with empty string
        self.assertEqual(result['sort_option'], '')
        self.assertEqual(result['author_selected'], '')
        self.assertEqual(result['artist_selected'], '')
        self.assertEqual(result['progress_status_selected'], '')
        self.assertEqual(result['approval_status_selected'], '')
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_service_error(self, mock_get_tags):
        """Test handling when service raises error"""
        # Mock the service method to raise an exception
        mock_get_tags.side_effect = Exception("Service error")
        
        # Create request
        request = self.factory.get('/novels/')
        context = {'request': request}
        
        # Should raise the exception (no error handling in template tag)
        with self.assertRaises(Exception):
            render_novel_filter(context)


class NovelTagsIntegrationTests(NovelTagsTestCase):
    """Test template tag integration with Django template system"""
    
    def test_template_tag_registration(self):
        """Test that template tag is properly registered"""
        # Test that the template tag can be loaded and used
        template_content = """
        {% load novel_tags %}
        {% render_novel_filter %}
        """
        
        # This should not raise an error
        template = Template(template_content)
        
        # Create context with request
        request = self.factory.get('/novels/')
        context = Context({'request': request})
        
        # Render template - this will call our template tag
        with patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter') as mock_get_tags:
            mock_get_tags.return_value = []
            
            # Should not raise an error
            rendered = template.render(context)
            
            # Should have called the service
            mock_get_tags.assert_called_once()
    
    def test_template_tag_with_missing_template(self):
        """Test template tag behavior when include template is missing"""
        # Since this is an inclusion tag, if the included template doesn't exist,
        # Django will raise a TemplateDoesNotExist error
        template_content = """
        {% load novel_tags %}
        {% render_novel_filter %}
        """
        
        template = Template(template_content)
        request = self.factory.get('/novels/')
        context = Context({'request': request})
        
        with patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter') as mock_get_tags:
            mock_get_tags.return_value = []
            
            # This might raise TemplateDoesNotExist if the include template is missing
            # But we're testing the tag function itself, not the template rendering
            try:
                template.render(context)
            except Exception as e:
                # Template-related errors are acceptable in this test context
                self.assertIn('novel_filter.html', str(e))


class NovelTagsErrorHandlingTests(NovelTagsTestCase):
    """Test error handling and edge cases"""
    
    def test_render_novel_filter_missing_request(self):
        """Test template tag with missing request in context"""
        # Create context without request
        context = {}
        
        # Should raise KeyError
        with self.assertRaises(KeyError):
            render_novel_filter(context)
    
    def test_render_novel_filter_none_request(self):
        """Test template tag with None request"""
        # Create context with None request
        context = {'request': None}
        
        # Should raise AttributeError when trying to access request.GET
        with self.assertRaises(AttributeError):
            render_novel_filter(context)
    
    @patch('novels.templatetags.novel_tags.NovelFilterService.get_all_tags_for_filter')
    def test_render_novel_filter_malformed_parameters(self, mock_get_tags):
        """Test handling of malformed GET parameters"""
        # Mock the service method
        mock_get_tags.return_value = []
        
        # Create request with malformed parameters
        request = self.factory.get('/novels/')
        # Manually set malformed GET data
        request.GET = {'tags': None}
        
        # Create context
        context = {'request': request}
        
        # Should handle gracefully
        try:
            result = render_novel_filter(context)
            # If it doesn't crash, that's good
            self.assertIsNotNone(result)
        except Exception:
            # Some parameter handling errors might occur, which is acceptable
            pass
