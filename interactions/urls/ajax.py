from django.urls import path
from .. import views

urlpatterns = [
    path("notifications/load_more/",
        views.load_more_notifications,
        name="notifications_load_more"
    ),
    
    path('notifications/<int:pk>/mark_read/',
        views.notification_mark_read,
        name='notification_mark_read'
    ),
    path("<slug:novel_slug>/comments/", views.novel_comments, name="novel_comments"),
    path('<slug:novel_slug>/reviews/', views.novel_reviews, name='novel_reviews'),
    path('<slug:novel_slug>/reviews/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review'
    ),
    path('<slug:novel_slug>/reviews/<int:review_id>/edit/',
        views.edit_review,
        name='edit_review'
    ),
    path('<slug:novel_slug>/reviews/create/',
        views.create_review,
        name='create_review'
    ),
]
