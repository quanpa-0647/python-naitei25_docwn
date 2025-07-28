from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'accounts'

urlpatterns = [
    path("", lambda request: HttpResponse("Accounts Home")),
    # Authentication URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Password Reset URLs
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
]
