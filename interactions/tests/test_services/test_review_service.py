from django.test import TestCase
from django.core.paginator import Paginator
from django.http import Http404
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from interactions.models import Review
from novels.models import Novel
from interactions.services import ReviewService
from interactions.forms import ReviewForm
from constants import PAGINATOR_REVIEW_LIST, MIN_RATE, MAX_RATE

User = get_user_model()


class TestReviewService(TestCase):
    
    def setUp(self):
        """Setup real test data"""
        # Create real users for testing
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            username='staffuser',
            password='testpass123',
            is_staff=True
        )
        
        # Create real novels for testing
        self.novel1 = Novel.objects.create(
            name='Test Novel 1',
            summary='Test summary 1',
            created_by=self.user1
        )
        
        self.novel2 = Novel.objects.create(
            name='Test Novel 2',
            summary='Test summary 2',
            created_by=self.user2
        )
        
        # Create some reviews for testing
        self.review1 = Review.objects.create(
            user=self.user1,
            novel=self.novel1,
            rating=5,
            content='Excellent novel!'
        )
        
        self.review2 = Review.objects.create(
            user=self.user2,
            novel=self.novel1,
            rating=3,
            content='Good novel'
        )
        
        self.review3 = Review.objects.create(
            user=self.user1,
            novel=self.novel2,
            rating=4,
            content='Pretty good'
        )
    
    def test_get_novel_reviews_data_with_rating_filter(self):
        """Test get_novel_reviews_data with rating filter"""
        result = ReviewService.get_novel_reviews_data(self.novel1.slug, rating_filter='5')
        
        self.assertEqual(result['novel'], self.novel1)
        self.assertEqual(result['total_reviews'], 1)  # Only one 5-star review
        self.assertEqual(result['rating_filter'], '5')
    
    def test_get_novel_reviews_data_novel_not_found(self):
        """Test get_novel_reviews_data raises Http404 when novel not found"""
        with self.assertRaises(Http404):
            ReviewService.get_novel_reviews_data('non-existent-novel')
    
    def test_get_novel_reviews_queryset_no_filter(self):
        """Test _get_novel_reviews_queryset without rating filter"""
        queryset = ReviewService._get_novel_reviews_queryset(self.novel1)
        
        # Should return all active reviews for novel1, ordered by -created_at
        reviews = list(queryset)
        self.assertEqual(len(reviews), 2)
        self.assertIn(self.review1, reviews)
        self.assertIn(self.review2, reviews)
        # Check ordering - newer reviews first
        self.assertTrue(reviews[0].created_at >= reviews[1].created_at)
    
    def test_get_novel_reviews_queryset_with_valid_filter(self):
        """Test _get_novel_reviews_queryset with valid rating filter"""
        queryset = ReviewService._get_novel_reviews_queryset(self.novel1, '5')
        
        reviews = list(queryset)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0], self.review1)  # Only the 5-star review
    
    def test_get_novel_reviews_queryset_with_invalid_filter(self):
        """Test _get_novel_reviews_queryset with invalid rating filter"""
        queryset = ReviewService._get_novel_reviews_queryset(self.novel1, 'invalid')
        
        # Should return all reviews (filter ignored)
        reviews = list(queryset)
        self.assertEqual(len(reviews), 2)
    
    def test_get_novel_reviews_queryset_with_out_of_range_filter(self):
        """Test _get_novel_reviews_queryset with out of range rating filter"""
        queryset = ReviewService._get_novel_reviews_queryset(self.novel1, str(MAX_RATE + 1))
        
        # Should return all reviews (filter ignored)
        reviews = list(queryset)
        self.assertEqual(len(reviews), 2)
    
    def test_get_user_reviews_data_success(self):
        """Test get_user_reviews_data returns correct data"""
        result = ReviewService.get_user_reviews_data(self.user1.pk)
        
        self.assertEqual(result['reviewed_user'], self.user1)
        self.assertEqual(result['rating_filter'], None)
        self.assertEqual(list(result['rating_choices']), list(range(MIN_RATE + 1, MAX_RATE + 1)))
        
        # Check that page_obj contains user1's reviews
        reviews_in_page = list(result['page_obj'])
        user1_reviews = [self.review1, self.review3]
        self.assertEqual(len(reviews_in_page), len(user1_reviews))
        for review in reviews_in_page:
            self.assertIn(review, user1_reviews)
    
    def test_get_user_reviews_data_with_rating_filter(self):
        """Test get_user_reviews_data with rating filter"""
        result = ReviewService.get_user_reviews_data(self.user1.pk, rating_filter='5')
        
        self.assertEqual(result['rating_filter'], '5')
        
        # Should only contain user1's 5-star reviews
        reviews_in_page = list(result['page_obj'])
        self.assertEqual(len(reviews_in_page), 1)
        self.assertEqual(reviews_in_page[0], self.review1)
    
    def test_get_user_reviews_data_user_not_found(self):
        """Test get_user_reviews_data raises Http404 when user not found"""
        with self.assertRaises(Http404):
            ReviewService.get_user_reviews_data(999999)
    
    def test_get_all_reviews_data_no_filters(self):
        """Test get_all_reviews_data without filters"""
        result = ReviewService.get_all_reviews_data()
        
        self.assertIsNone(result['search'])
        self.assertIsNone(result['rating_filter'])
        self.assertEqual(list(result['rating_choices']), list(range(MIN_RATE + 1, MAX_RATE + 1)))
        
        # Should contain all active reviews
        all_reviews = list(result['page_obj'])
        expected_reviews = [self.review1, self.review2, self.review3]
        self.assertEqual(len(all_reviews), len(expected_reviews))
        for review in all_reviews:
            self.assertIn(review, expected_reviews)
    
    def test_get_all_reviews_data_with_search(self):
        """Test get_all_reviews_data with search filter"""
        # Search for reviews containing "excellent"
        result = ReviewService.get_all_reviews_data(search='excellent')
        
        self.assertEqual(result['search'], 'excellent')
        
        reviews_in_page = list(result['page_obj'])
        self.assertEqual(len(reviews_in_page), 1)
        self.assertEqual(reviews_in_page[0], self.review1)
    
    def test_get_all_reviews_data_with_rating_filter(self):
        """Test get_all_reviews_data with rating filter"""
        result = ReviewService.get_all_reviews_data(rating_filter='4')
        
        self.assertEqual(result['rating_filter'], '4')
        
        reviews_in_page = list(result['page_obj'])
        self.assertEqual(len(reviews_in_page), 1)
        self.assertEqual(reviews_in_page[0], self.review3)
    
    def test_get_review_detail_success(self):
        """Test get_review_detail returns correct review"""
        result = ReviewService.get_review_detail(self.review1.id)
        
        self.assertEqual(result, self.review1)
    
    def test_get_review_detail_not_found(self):
        """Test get_review_detail raises Http404 when review not found"""
        with self.assertRaises(Http404):
            ReviewService.get_review_detail(999999)
    
    def test_create_review_success(self):
        """Test create_review with valid data"""
        # Create a new user who hasn't reviewed novel1 yet
        new_user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            password='testpass123'
        )
        
        data = {
            'rating': '4',
            'content': 'Great story!'
        }
        
        initial_count = Review.objects.count()
        result = ReviewService.create_review(new_user, self.novel1.slug, data)
        
        # Should return the created review
        self.assertIsInstance(result, Review)
        self.assertEqual(Review.objects.count(), initial_count + 1)
        self.assertEqual(result.rating, 4)
        self.assertEqual(result.content, 'Great story!')
        self.assertEqual(result.user, new_user)
        self.assertEqual(result.novel, self.novel1)
    
    def test_create_review_duplicate(self):
        """Test create_review with duplicate review"""
        data = {
            'rating': '4',
            'content': 'Another review'
        }
        
        # user1 already has a review for novel1
        with self.assertRaises(IntegrityError) as cm:
            ReviewService.create_review(self.user1, self.novel1.slug, data)
        
        self.assertEqual(str(cm.exception), 'duplicate')
    
    def test_create_review_form_invalid(self):
        """Test create_review with invalid form data"""
        new_user = User.objects.create_user(
            email='newuser2@example.com',
            username='newuser2',
            password='testpass123'
        )
        
        # Empty content should be invalid
        data = {
            'rating': '4',
            'content': ''
        }
        
        result = ReviewService.create_review(new_user, self.novel1.slug, data)
        
        # Should return form errors
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
    
    def test_create_review_novel_not_found(self):
        """Test create_review with non-existent novel"""
        new_user = User.objects.create_user(
            email='newuser3@example.com',
            username='newuser3',
            password='testpass123'
        )
        
        data = {
            'rating': '4',
            'content': 'Great story!'
        }
        
        with self.assertRaises(Http404):
            ReviewService.create_review(new_user, 'non-existent-novel', data)
    
    def test_edit_review_success(self):
        """Test edit_review with valid data and permissions"""
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, '3', 'Updated content'
        )
        
        self.assertEqual(status, 'ok')
        self.assertEqual(review, self.review1)
        
        # Refresh from database
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 3)
        self.assertEqual(self.review1.content, 'Updated content')
    
    def test_edit_review_forbidden(self):
        """Test edit_review with insufficient permissions"""
        # user2 trying to edit user1's review
        review, status = ReviewService.edit_review(
            self.user2, self.novel1.slug, self.review1.id, '3', 'Updated content'
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'forbidden')
        
        # Original review should be unchanged
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 5)
        self.assertEqual(self.review1.content, 'Excellent novel!')
    
    def test_edit_review_staff_permission(self):
        """Test edit_review with staff user permissions"""
        original_content = self.review1.content
        
        review, status = ReviewService.edit_review(
            self.staff_user, self.novel1.slug, self.review1.id, '2', 'Staff edited'
        )
        
        self.assertEqual(status, 'ok')
        self.assertEqual(review, self.review1)
        
        # Refresh from database
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 2)
        self.assertEqual(self.review1.content, 'Staff edited')
    
    def test_edit_review_empty_content(self):
        """Test edit_review with empty content"""
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, '4', ''
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'empty')
    
    def test_edit_review_invalid_rating(self):
        """Test edit_review with invalid rating"""
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, 'invalid', 'Updated content'
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'invalid_rating')
    
    def test_edit_review_rating_out_of_range(self):
        """Test edit_review with rating out of valid range"""
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, str(MAX_RATE + 1), 'Updated content'
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'invalid_rating')
        
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, str(MIN_RATE), 'Updated content'
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'invalid_rating')
    
    def test_edit_review_content_too_long(self):
        """Test edit_review with content exceeding max length"""
        long_content = 'x' * 2001
        
        review, status = ReviewService.edit_review(
            self.user1, self.novel1.slug, self.review1.id, '4', long_content
        )
        
        self.assertIsNone(review)
        self.assertEqual(status, 'too_long')
    
    def test_edit_review_not_found(self):
        """Test edit_review with non-existent review"""
        with self.assertRaises(Http404):
            ReviewService.edit_review(
                self.user1, self.novel1.slug, 999999, '4', 'Updated content'
            )
    
    def test_edit_review_novel_not_found(self):
        """Test edit_review with non-existent novel"""
        with self.assertRaises(Http404):
            ReviewService.edit_review(
                self.user1, 'non-existent-novel', self.review1.id, '4', 'Updated content'
            )
    
    def test_delete_review_success(self):
        """Test delete_review successfully soft deletes review"""
        self.assertTrue(self.review1.is_active)
        
        result = ReviewService.delete_review(self.novel1.slug, self.review1.id)
        
        self.assertEqual(result, True)
    
    def test_delete_review_not_found(self):
        """Test delete_review with non-existent review"""
        with self.assertRaises(Http404):
            ReviewService.delete_review(self.novel1.slug, 999999)
    
    def test_delete_review_novel_not_found(self):
        """Test delete_review with non-existent novel"""
        with self.assertRaises(Http404):
            ReviewService.delete_review('non-existent-novel', self.review1.id)
    
    def test_has_user_reviewed_novel_true(self):
        """Test has_user_reviewed_novel returns True when user has reviewed"""
        result = ReviewService.has_user_reviewed_novel(self.user1, self.novel1)
        self.assertTrue(result)
    
    def test_has_user_reviewed_novel_false(self):
        """Test has_user_reviewed_novel returns False when user hasn't reviewed"""
        new_user = User.objects.create_user(
            email='newuser4@example.com',
            username='newuser4',
            password='testpass123'
        )
        
        result = ReviewService.has_user_reviewed_novel(new_user, self.novel1)
        self.assertFalse(result)
    
    def test_has_user_reviewed_novel_inactive_review(self):
        """Test has_user_reviewed_novel returns False for inactive reviews"""
        # Create an inactive review
        inactive_review = Review.objects.create(
            user=self.user2,
            novel=self.novel2,
            rating=3,
            content='Test review',
            is_active=False
        )
        
        result = ReviewService.has_user_reviewed_novel(self.user2, self.novel2)
        self.assertFalse(result)
    
    def test_pagination_functionality(self):
        """Test that pagination works correctly with large datasets"""
        # Create a new novel for this test
        test_novel = Novel.objects.create(
            name='Pagination Test Novel',
            summary='Test pagination',
            created_by=self.user1
        )
        
        # Create many users and reviews
        users_and_reviews = []
        for i in range(15):  # Create 15 reviews (more than default pagination)
            user = User.objects.create_user(
                email=f'user{i+10}@example.com',
                username=f'user{i+10}',
                password='testpass123'
            )
            review = Review.objects.create(
                user=user,
                novel=test_novel,
                rating=(i % 5) + 1,  # Ratings from 1-5
                content=f'Review content {i}'
            )
            users_and_reviews.append((user, review))
        
        # Test first page
        result = ReviewService.get_novel_reviews_data(test_novel.slug, page=1)
        
        self.assertEqual(result['total_reviews'], 15)
        first_page_reviews = list(result['page_obj'])
        self.assertEqual(len(first_page_reviews), min(PAGINATOR_REVIEW_LIST, 15))
        
        # Test second page if there is one
        if result['page_obj'].has_next():
            result_page2 = ReviewService.get_novel_reviews_data(test_novel.slug, page=2)
            second_page_reviews = list(result_page2['page_obj'])
            
            # Ensure no overlap between pages
            first_page_ids = {r.id for r in first_page_reviews}
            second_page_ids = {r.id for r in second_page_reviews}
            self.assertEqual(len(first_page_ids.intersection(second_page_ids)), 0)
    
    def test_rating_filter_edge_cases(self):
        """Test rating filter with various edge cases"""
        # Test with minimum valid rating
        result = ReviewService.get_novel_reviews_data(
            self.novel1.slug, rating_filter=str(MIN_RATE + 1)
        )
        # Should work without error
        self.assertIsNotNone(result['page_obj'])
        
        # Test with maximum valid rating
        result = ReviewService.get_novel_reviews_data(
            self.novel1.slug, rating_filter=str(MAX_RATE)
        )
        # Should work without error
        self.assertIsNotNone(result['page_obj'])
        
        # Test with negative rating
        result = ReviewService.get_novel_reviews_data(
            self.novel1.slug, rating_filter='-1'
        )
        # Should return all reviews (filter ignored)
        self.assertEqual(result['total_reviews'], 2)
        
        # Test with zero rating
        result = ReviewService.get_novel_reviews_data(
            self.novel1.slug, rating_filter='0'
        )
        # Should return all reviews (filter ignored)
        self.assertEqual(result['total_reviews'], 2)
