from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from interactions.forms import ReviewForm, ReviewDeleteForm
from interactions.models import Review
from novels.models import Novel
from constants import MIN_RATE, MAX_RATE

User = get_user_model()


class ReviewFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="tester",
            password="password123"
        )
        self.novel = Novel.objects.create(
            name="My Novel",
            summary="Summary here",
            created_by=self.user
        )

    def test_review_form_valid(self):
        """Test valid review form"""
        form = ReviewForm(
            data={"rating": 5, "content": "Great novel!"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_empty_content(self):
        """Test form with empty content"""
        form = ReviewForm(
            data={"rating": 4, "content": ""},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_review_form_invalid_whitespace_only_content(self):
        """Test form with whitespace-only content"""
        form = ReviewForm(
            data={"rating": 4, "content": "   \n\t  "},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_review_form_invalid_rating_too_low(self):
        """Test form with rating below minimum"""
        form = ReviewForm(
            data={"rating": MIN_RATE, "content": "Bad novel"},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_invalid_rating_too_high(self):
        """Test form with rating above maximum"""
        form = ReviewForm(
            data={"rating": MAX_RATE + 1, "content": "Amazing novel"},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_valid_minimum_rating(self):
        """Test form with minimum valid rating"""
        form = ReviewForm(
            data={"rating": MIN_RATE + 1, "content": "Not great"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())

    def test_review_form_valid_maximum_rating(self):
        """Test form with maximum valid rating"""
        form = ReviewForm(
            data={"rating": MAX_RATE, "content": "Excellent"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())

    def test_review_form_content_max_length(self):
        """Test form with content at maximum length"""
        max_content = "x" * 2000
        form = ReviewForm(
            data={"rating": 5, "content": max_content},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())

    def test_review_form_content_exceeds_max_length(self):
        """Test form with content exceeding maximum length"""
        long_content = "x" * 2001
        form = ReviewForm(
            data={"rating": 5, "content": long_content},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_review_form_missing_rating(self):
        """Test form with missing rating"""
        form = ReviewForm(
            data={"content": "Great novel!"},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_invalid_rating_string(self):
        """Test form with non-numeric rating"""
        form = ReviewForm(
            data={"rating": "invalid", "content": "Great novel!"},
            user=self.user,
            novel=self.novel,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_review_form_save_assigns_user_and_novel(self):
        """Test form save assigns user and novel correctly"""
        form = ReviewForm(
            data={"rating": 3, "content": "ok"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.novel, self.novel)
        self.assertIsInstance(instance, Review)

    def test_review_form_save_with_commit_true(self):
        """Test form save with commit=True"""
        form = ReviewForm(
            data={"rating": 4, "content": "Good novel"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())
        
        # Count reviews before saving
        initial_count = Review.objects.count()
        
        instance = form.save(commit=True)
        
        # Check that review was actually saved to database
        self.assertEqual(Review.objects.count(), initial_count + 1)
        self.assertTrue(Review.objects.filter(id=instance.id).exists())

    def test_review_form_save_without_user_novel(self):
        """Test form save without user and novel in constructor"""
        form = ReviewForm(
            data={"rating": 4, "content": "Good novel"}
        )
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)

    def test_review_form_widget_attributes(self):
        """Test form widget attributes are set correctly"""
        form = ReviewForm(user=self.user, novel=self.novel)
        
        # Check rating widget attributes
        rating_widget = form.fields['rating'].widget
        self.assertIn('form-select', rating_widget.attrs['class'])
        self.assertIn('rating-select', rating_widget.attrs['class'])
        
        # Check content widget attributes
        content_widget = form.fields['content'].widget
        self.assertIn('form-control', content_widget.attrs['class'])
        self.assertIn('placeholder', content_widget.attrs)
        self.assertEqual(content_widget.attrs['rows'], 5)

    def test_review_form_rating_choices(self):
        """Test form rating field has correct choices"""
        form = ReviewForm(user=self.user, novel=self.novel)
        rating_field = form.fields['rating']
        
        # Check that choices are set correctly
        expected_choices = [(i, f"{i} sao") for i in range(MIN_RATE + 1, MAX_RATE + 1)]
        self.assertEqual(rating_field.widget.choices, expected_choices)

    def test_review_form_content_strips_whitespace(self):
        """Test form content field strips whitespace"""
        form = ReviewForm(
            data={"rating": 5, "content": "  Great novel!  \n\t"},
            user=self.user,
            novel=self.novel,
        )
        self.assertTrue(form.is_valid())
        cleaned_content = form.clean_content()
        self.assertEqual(cleaned_content, "Great novel!")

    def test_review_form_fields_labels_and_help_text(self):
        """Test form fields have correct labels and help text"""
        form = ReviewForm(user=self.user, novel=self.novel)
        
        # Check rating field
        rating_field = form.fields['rating']
        self.assertEqual(str(rating_field.label), "Đánh giá")
        self.assertIn(f"từ {MIN_RATE + 1}-{MAX_RATE} sao", str(rating_field.help_text))
        
        # Check content field
        content_field = form.fields['content']
        self.assertEqual(str(content_field.label), "Nội dung đánh giá")
        self.assertEqual(str(content_field.help_text), "Tối đa 2000 ký tự")


class ReviewDeleteFormTest(TestCase):
    def test_review_delete_form_valid(self):
        """Test valid delete form"""
        form = ReviewDeleteForm(data={'confirm': True})
        self.assertTrue(form.is_valid())

    def test_review_delete_form_invalid_without_confirm(self):
        """Test delete form without confirmation"""
        form = ReviewDeleteForm(data={'confirm': False})
        self.assertFalse(form.is_valid())
        self.assertIn('confirm', form.errors)

    def test_review_delete_form_invalid_missing_confirm(self):
        """Test delete form with missing confirm field"""
        form = ReviewDeleteForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('confirm', form.errors)

    def test_review_delete_form_widget_attributes(self):
        """Test delete form widget attributes"""
        form = ReviewDeleteForm()
        confirm_widget = form.fields['confirm'].widget
        self.assertIn('form-check-input', confirm_widget.attrs['class'])

    def test_review_delete_form_field_label(self):
        """Test delete form field label"""
        form = ReviewDeleteForm()
        confirm_field = form.fields['confirm']
        self.assertEqual(str(confirm_field.label), "Tôi xác nhận muốn xóa đánh giá này")
