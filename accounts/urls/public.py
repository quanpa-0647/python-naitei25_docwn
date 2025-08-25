from django.urls import path
from django.http import HttpResponse
from accounts.views.public import *

urlpatterns = [
    path("", lambda request: HttpResponse("Accounts Home")),
    # Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Profile URLs
    path('profile/<str:username>/', profile_detail_view, name='profile'), 
    path('profile/<str:username>/edit/', profile_edit_view, name='profile_edit'),
    
    # Password URLs
    path('change-password/', change_password_view, name='change_password'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', reset_password_view, name='reset_password'),
]
