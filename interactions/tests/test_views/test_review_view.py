import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from unittest.mock import patch, Mock, MagicMock
from http import HTTPStatus
from datetime import datetime
from interactions.views import novel_reviews, create_review, edit_review, delete_review
from novels.models import Novel
from interactions.models import Review
from constants import DEFAULT_PAGE_NUMBER, PAGINATOR_REVIEW_LIST, MIN_RATE, MAX_RATE

User = get_user_model()


class TestNovelReviewsView(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.factory = RequestFactory()
        self.novel_slug = 'test-novel'
        
        # Mock novel
        self.mock_novel = Mock(spec=Novel)
        self.mock_novel.slug = self.novel_slug
        
        # Mock user and profile
        self.mock_profile = Mock()
        self.mock_profile.get_avatar.return_value = 'http://example.com/avatar.jpg'
        
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.username = 'testuser'
        self.mock_user.profile = self.mock_profile
        
        # Mock review
        self.mock_review = Mock(spec=Review)
        self.mock_review.id = 1
        self.mock_review.rating = 5
        self.mock_review.content = 'Great novel!'
        self.mock_review.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.mock_review.user = self.mock_user
        
        # Mock paginator and page object
        self.mock_page_obj = Mock()
        self.mock_page_obj.has_next.return_value = True
        self.mock_page_obj.__iter__ = Mock(return_value=iter([self.mock_review]))
        
        self.mock_paginator = Mock()
        self.mock_paginator.count = 1
        self.mock_paginator.get_page.return_value = self.mock_page_obj
    
    @patch('interactions.views.public.review_view.ReviewService.get_novel_reviews_data')
    def test_novel_reviews_success_default_params(self, mock_get_reviews_data):
        """Test novel_reviews view with default parameters"""
        # Setup mock return data
        mock_get_reviews_data.return_value = {
            'page_obj': self.mock_page_obj,
            'total_reviews': 1
        }
        
        # Create request
        request = self.factory.get(f'/interactions/ajax/{self.novel_slug}/reviews/')
        
        # Call view
        response = novel_reviews(request, self.novel_slug)
        
        # Assertions
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Check response data
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['reviews']), 1)
        self.assertEqual(response_data['reviews'][0]['id'], 1)
        self.assertEqual(response_data['reviews'][0]['rating'], 5)
        self.assertEqual(response_data['reviews'][0]['content'], 'Great novel!')
        self.assertEqual(response_data['total_reviews'], 1)
        self.assertTrue(response_data['has_next'])
        
        # Verify filters
        self.assertEqual(response_data['filters']['rating'], '')
        self.assertEqual(response_data['filters']['sort'], '-created_at')
        
        # Verify service was called correctly
        mock_get_reviews_data.assert_called_once_with(
            novel_slug=self.novel_slug,
            rating_filter='',
            page=DEFAULT_PAGE_NUMBER
        )
    
    @patch('interactions.views.public.review_view.ReviewService.get_novel_reviews_data')
    def test_novel_reviews_with_rating_filter(self, mock_get_reviews_data):
        """Test novel_reviews view with rating filter"""
        mock_get_reviews_data.return_value = {
            'page_obj': self.mock_page_obj,
            'total_reviews': 1
        }
        
        # Create request with rating filter
        request = self.factory.get(f'/interactions/ajax/{self.novel_slug}/reviews/?rating=5')
        
        # Call view
        response = novel_reviews(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['filters']['rating'], '5')
        
        # Verify service was called with rating filter
        mock_get_reviews_data.assert_called_once_with(
            novel_slug=self.novel_slug,
            rating_filter='5',
            page=DEFAULT_PAGE_NUMBER
        )
    
    @patch('interactions.views.public.review_view.ReviewService.get_novel_reviews_data')
    def test_novel_reviews_with_pagination(self, mock_get_reviews_data):
        """Test novel_reviews view with pagination"""
        mock_get_reviews_data.return_value = {
            'page_obj': self.mock_page_obj,
            'total_reviews': 1
        }
        
        # Create request with page parameter
        request = self.factory.get(f'/interactions/ajax/{self.novel_slug}/reviews/?page=3')
        
        # Call view
        response = novel_reviews(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verify pagination
        mock_get_reviews_data.assert_called_once_with(
            novel_slug=self.novel_slug,
            rating_filter='',
            page=3
        )
    
    @patch('interactions.views.public.review_view.ReviewService.get_novel_reviews_data')
    def test_novel_reviews_service_exception(self, mock_get_reviews_data):
        """Test novel_reviews view handles service exceptions"""
        # Setup mock to raise exception
        mock_get_reviews_data.side_effect = Exception("Service error")
        
        # Create request
        request = self.factory.get(f'/interactions/ajax/{self.novel_slug}/reviews/')
        
        # Call view
        response = novel_reviews(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], "Service error")
    
    @patch('interactions.views.public.review_view.ReviewService.get_novel_reviews_data')
    def test_novel_reviews_empty_results(self, mock_get_reviews_data):
        """Test novel_reviews view with no reviews"""
        # Mock empty page
        empty_page_obj = Mock()
        empty_page_obj.has_next.return_value = False
        empty_page_obj.__iter__ = Mock(return_value=iter([]))
        
        mock_get_reviews_data.return_value = {
            'page_obj': empty_page_obj,
            'total_reviews': 0
        }
        
        # Create request
        request = self.factory.get(f'/interactions/ajax/{self.novel_slug}/reviews/')
        
        # Call view
        response = novel_reviews(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(len(response_data['reviews']), 0)
        self.assertEqual(response_data['total_reviews'], 0)
        self.assertFalse(response_data['has_next'])


class TestCreateReviewView(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.factory = RequestFactory()
        self.novel_slug = 'test-novel'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Mock novel
        self.mock_novel = Mock(spec=Novel)
        self.mock_novel.slug = self.novel_slug
        self.mock_novel.title = 'Test Novel'
        self.mock_novel.created_by = self.user
        
        # Mock review
        self.mock_review = Mock(spec=Review)
        self.mock_review.id = 1
        self.mock_review.rating = 5
        self.mock_review.content = 'Great novel!'
        self.mock_review.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.mock_review.user = self.user
    
    @patch('interactions.views.public.review_view.async_to_sync')
    @patch('interactions.views.public.review_view.NotificationService.create_notification')
    @patch('interactions.views.public.review_view.Novel.objects.get')
    @patch('interactions.views.public.review_view.ReviewService.create_review')
    def test_create_review_success(self, mock_create_review, mock_novel_get, mock_create_notification, mock_async_to_sync):
        """Test successful review creation"""
        # Setup mocks
        mock_create_review.return_value = self.mock_review
        mock_novel_get.return_value = self.mock_novel
        mock_create_notification.return_value = Mock()
        
        # Create request with form data
        form_data = {
            'rating': '5',
            'content': 'Great novel!'
        }
        request = self.factory.post(f'/interactions/ajax/{self.novel_slug}/reviews/', data=form_data)
        request.user = self.user
        
        # Call view
        response = create_review(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        self.assertIn('review', response_data)
        
        # Verify notification was created
        mock_create_notification.assert_called_once()
    
    @patch('interactions.views.public.review_view.ReviewService.create_review')
    def test_create_review_integrity_error(self, mock_create_review):
        """Test review creation with duplicate review error"""
        from django.db import IntegrityError
        
        # Setup mock to raise IntegrityError
        mock_create_review.side_effect = IntegrityError("duplicate")
        
        # Create request
        form_data = {
            'rating': '5',
            'content': 'Great novel!'
        }
        request = self.factory.post(f'/interactions/ajax/{self.novel_slug}/reviews/', data=form_data)
        request.user = self.user
        
        # Call view
        response = create_review(request, self.novel_slug)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)


class TestEditReviewView(TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.factory = RequestFactory()
        self.novel_slug = 'test-novel'
        self.review_id = 1
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Mock review
        self.mock_review = Mock(spec=Review)
        self.mock_review.id = 1
        self.mock_review.rating = 5
        self.mock_review.content = 'Updated content'
        self.mock_review.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.mock_review.user = self.user
    
    @patch('interactions.views.public.review_view.ReviewService.edit_review')
    def test_edit_review_success(self, mock_edit_review):
        """Test successful review edit"""
        # Setup mock
        mock_edit_review.return_value = (self.mock_review, "ok")
        
        # Create request with JSON data
        json_data = {
            'rating': 5,
            'content': 'Updated content'
        }
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data=json.dumps(json_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        self.assertIn('review', response_data)
        
        # Verify service was called
        mock_edit_review.assert_called_once_with(
            self.user, self.novel_slug, self.review_id, 5, 'Updated content'
        )
    
    @patch('interactions.views.public.review_view.ReviewService.edit_review')
    def test_edit_review_forbidden(self, mock_edit_review):
        """Test edit review with forbidden access"""
        # Setup mock
        mock_edit_review.return_value = (None, "forbidden")
        
        # Create request
        json_data = {
            'rating': 5,
            'content': 'Updated content'
        }
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data=json.dumps(json_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
    
    @patch('interactions.views.public.review_view.ReviewService.edit_review')
    def test_edit_review_empty_content(self, mock_edit_review):
        """Test edit review with empty content"""
        # Setup mock
        mock_edit_review.return_value = (None, "empty")
        
        # Create request
        json_data = {
            'rating': 5,
            'content': ''
        }
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data=json.dumps(json_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
    
    @patch('interactions.views.public.review_view.ReviewService.edit_review')
    def test_edit_review_invalid_rating(self, mock_edit_review):
        """Test edit review with invalid rating"""
        # Setup mock
        mock_edit_review.return_value = (None, "invalid_rating")
        
        # Create request
        json_data = {
            'rating': 'invalid',
            'content': 'Updated content'
        }
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data=json.dumps(json_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
    
    @patch('interactions.views.public.review_view.ReviewService.edit_review')
    def test_edit_review_content_too_long(self, mock_edit_review):
        """Test edit review with content too long"""
        # Setup mock
        mock_edit_review.return_value = (None, "too_long")
        
        # Create request
        json_data = {
            'rating': 5,
            'content': 'x' * 2001  # Too long content
        }
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data=json.dumps(json_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
    
    def test_edit_review_invalid_json(self):
        """Test edit review with invalid JSON data"""
        # Create request with invalid JSON
        request = self.factory.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/edit/',
            data='invalid json',
            content_type='application/json'
        )
        request.user = self.user
        
        # Call view
        response = edit_review(request, self.novel_slug, self.review_id)
        
        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)


class TestDeleteReviewView(TestCase):

    def setUp(self):
        """Setup test data"""
        self.novel_slug = 'test-novel'
        self.review_id = 1
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        # Mock review
        self.mock_review = Mock(spec=Review)
        self.mock_review.id = 1
        self.mock_review.user = self.user

    @patch('interactions.views.public.review_view.ReviewService.get_review_detail')
    @patch('interactions.views.public.review_view.ReviewService.delete_review')
    def test_delete_review_success(self, mock_delete_review, mock_get_review_detail):
        """Test successful review deletion"""
        # Setup mock
        mock_get_review_detail.return_value = self.mock_review
        mock_delete_review.return_value = self.mock_review

        # Login user
        self.client.login(username='test@example.com', password='testpass123')

        # Gửi request qua test client
        response = self.client.post(
            f'/interactions/ajax/{self.novel_slug}/reviews/{self.review_id}/delete/'
        )

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)

        # Verify service was called
        mock_get_review_detail.assert_called_once_with(self.review_id)
        mock_delete_review.assert_called_once_with(self.novel_slug, self.review_id)


