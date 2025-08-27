import json
from http import HTTPStatus
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from interactions.services import ReviewService, NotificationService
from common.decorators import require_login, require_owner_or_admin
from novels.models import Novel
from common.utils import send_notification_to_user
from asgiref.sync import async_to_sync
from django.db import IntegrityError
from constants import (
    DEFAULT_PAGE_NUMBER,
    MIN_RATE,
    MAX_RATE,
    NotificationTypeChoices,
    MAX_LENGTH_REVIEW_CONTENT
)


@require_http_methods(["GET"])
def novel_reviews(request, novel_slug):
    """Danh sách review của 1 novel"""
    try:
        page = int(request.GET.get("page", DEFAULT_PAGE_NUMBER))
        rating_filter = request.GET.get("rating", "").strip()

        result = ReviewService.get_novel_reviews_data(
            novel_slug=novel_slug,
            rating_filter=rating_filter,
            page=page
        )

        reviews_data = []
        for review in result["page_obj"]:
            reviews_data.append({
                "id": review.id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat(),
                "user": {
                    "id": review.user.id,
                    "username": review.user.username,
                    "avatar_url": review.user.profile.get_avatar(),
                },
            })

        return JsonResponse({
            "success": True,
            "reviews": reviews_data,
            "has_next": result["page_obj"].has_next(),
            "total_reviews": result["total_reviews"],
            "filters": {
                "rating": rating_filter,
                "sort": "-created_at",  # mặc định service đang order '-created_at'
            },
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["POST"])
@require_login
def create_review(request, novel_slug):
    """Tạo mới review"""
    try:
        result = ReviewService.create_review(request.user, novel_slug, request.POST)
        novel = Novel.objects.get(slug=novel_slug)

        if isinstance(result, dict):  # form.errors
            return JsonResponse({
                "success": False,
                "message": _("Có lỗi trong dữ liệu. Vui lòng kiểm tra lại."),
                "errors": result,
            })

        review = result
        
        notification = NotificationService.create_notification(
            user=novel.created_by,
            title=_("Đánh giá mới"),
            content=_("Tiểu thuyết của bạn '%s' vừa nhận được đánh giá mới.") % novel.name,
            notification_type=NotificationTypeChoices.REVIEW,
            related_object=review
        )
        
        async_to_sync(send_notification_to_user)(
            user_id=novel.created_by.id,
            notification=notification,
            redirect_url=f"/novels/{novel.slug}/#reviews-list"
        )
        
        return JsonResponse({
            "success": True,
            "message": _("Đánh giá của bạn đã được thêm thành công!"),
            "review": {
                "id": review.id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat(),
                "user": {
                    "id": review.user.id,
                    "username": review.user.username,
                    "avatar_url": review.user.profile.get_avatar(),
                },
            },
        })
    except IntegrityError as e:
        print(e)
        if str(e) == "duplicate":
            return JsonResponse({
                "success": False,
                "message": _("Bạn đã đánh giá cuốn tiểu thuyết này rồi."),
            })
        else:
            return JsonResponse({
                "success": False,
                "message": _("Có lỗi xảy ra khi thêm đánh giá."),
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@require_http_methods(["POST"])
@require_login
def edit_review(request, novel_slug, review_id):
    """Chỉnh sửa review"""
    try:
        data = json.loads(request.body)
        rating = data.get("rating")
        content = data.get("content", "")

        review, status = ReviewService.edit_review(
            request.user, novel_slug, review_id, rating, content
        )

        if status == "forbidden":
            return JsonResponse({
                "success": False,
                "message": _("Bạn không có quyền chỉnh sửa đánh giá này."),
            }, status=HTTPStatus.FORBIDDEN)

        if status == "empty":
            return JsonResponse({
                "success": False,
                "message": _("Nội dung đánh giá không được để trống."),
            }, status=HTTPStatus.BAD_REQUEST)

        if status == "invalid_rating":
            return JsonResponse({
                "success": False,
                "message": _("Đánh giá phải từ %s đến %s sao.") % (MIN_RATE + 1, MAX_RATE),
            }, status=HTTPStatus.BAD_REQUEST)

        if status == "too_long":
            return JsonResponse({
                "success": False,
                "message": _(f"Nội dung đánh giá không được vượt quá {MAX_LENGTH_REVIEW_CONTENT} ký tự."),
            }, status=HTTPStatus.BAD_REQUEST)

        return JsonResponse({
            "success": True,
            "message": _("Đánh giá đã được cập nhật thành công!"),
            "review": {
                "id": review.id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat(),
                "user": {
                    "id": review.user.id,
                    "username": review.user.username,
                    "avatar_url": review.user.profile.get_avatar(),
                },
            },
        })
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": _("Dữ liệu không hợp lệ."),
        }, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        return JsonResponse({
            "success": False,
            "message": _("Có lỗi xảy ra khi cập nhật đánh giá."),
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@require_http_methods(["POST"])
@require_owner_or_admin(lambda request, *args, **kwargs: ReviewService.get_review_detail(kwargs["review_id"]))
def delete_review(request, novel_slug, review_id):
    """Xóa review"""
    ReviewService.delete_review(novel_slug, review_id)
    return JsonResponse({
        "success": True,
        "message": _("Đánh giá đã được xóa thành công!"),
    })
