from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from interactions.models import Review
from interactions.forms import ReviewForm
from novels.models import Novel
from constants import (
    PAGINATOR_REVIEW_LIST,
    MIN_RATE,
    MAX_RATE,
    MAX_LENGTH_REVIEW_CONTENT,
)


class ReviewService:
    @staticmethod
    def get_novel_reviews_data(novel_slug, rating_filter=None, page=1):
        novel = get_object_or_404(Novel, slug=novel_slug)
        reviews = ReviewService._get_novel_reviews_queryset(novel, rating_filter)
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        return {
            'novel': novel,
            'page_obj': page_obj,
            'rating_filter': rating_filter,
            'total_reviews': paginator.count,
        }

    @staticmethod
    def _get_novel_reviews_queryset(novel, rating_filter=None):
        reviews = Review.objects.select_related('user').filter(
            novel=novel,
            is_active=True
        ).order_by('-created_at')
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        return reviews

    @staticmethod
    def get_user_reviews_data(user_id, rating_filter=None, page=1):
        from accounts.models import User
        user = get_object_or_404(User, pk=user_id)
        reviews = Review.objects.select_related('novel').filter(
            user=user,
            is_active=True
        ).order_by('-created_at')
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        return {
            'reviewed_user': user,
            'avatar_url': user.profile.avatar_url,
            'page_obj': page_obj,
            'rating_filter': rating_filter,
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }

    @staticmethod
    def get_all_reviews_data(search=None, rating_filter=None, page=1):
        reviews = Review.objects.select_related('user', 'novel').filter(
            is_active=True
        ).order_by('-created_at')
        if search:
            reviews = reviews.filter(
                Q(content__icontains=search) |
                Q(novel__name__icontains=search) |
                Q(user__username__icontains=search)
            )
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if MIN_RATE < rating_value <= MAX_RATE:
                    reviews = reviews.filter(rating=rating_value)
            except (ValueError, TypeError):
                pass
        paginator = Paginator(reviews, PAGINATOR_REVIEW_LIST)
        page_obj = paginator.get_page(page)
        return {
            'page_obj': page_obj,
            'search': search,
            'rating_filter': rating_filter,
            'rating_choices': range(MIN_RATE + 1, MAX_RATE + 1),
        }

    @staticmethod
    def get_review_detail(review_pk):
        return get_object_or_404(
            Review.objects.select_related('user', 'novel'),
            pk=review_pk,
            is_active=True
        )

    @staticmethod
    def create_review(user, novel_slug, data):
        novel = get_object_or_404(Novel, slug=novel_slug, deleted_at__isnull=True)

        # kiểm tra duplicate
        if Review.objects.filter(user=user, novel=novel, is_active=True).exists():
            raise IntegrityError("duplicate")

        form = ReviewForm(data, user=user, novel=novel)
        if form.is_valid():
            return form.save()
        else:
            return form.errors

    @staticmethod
    def edit_review(user, novel_slug, review_id, rating, content):
        novel = get_object_or_404(Novel, slug=novel_slug, deleted_at__isnull=True)
        review = get_object_or_404(Review, pk=review_id, novel=novel, is_active=True)

        # permission
        if not (user == review.user or user.is_staff):
            return None, "forbidden"

        if not content:
            return None, "empty"

        try:
            rating_value = int(rating)
        except (TypeError, ValueError):
            return None, "invalid_rating"

        if not (MIN_RATE < rating_value <= MAX_RATE):
            return None, "invalid_rating"

        if len(content) > MAX_LENGTH_REVIEW_CONTENT:
            return None, "too_long"

        review.rating = rating_value
        review.content = content.strip()
        review.save()
        return review, "ok"

    @staticmethod
    def delete_review(novel_slug, review_id):
        novel = get_object_or_404(Novel, slug=novel_slug, deleted_at__isnull=True)
        review = get_object_or_404(Review, pk=review_id, novel=novel, is_active=True)
        review.delete()
        return True
    
    @staticmethod
    def has_user_reviewed_novel(user, novel):
        return Review.objects.filter(
            user=user,
            novel=novel,
            is_active=True
        ).exists()
