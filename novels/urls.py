from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
    path("", views.Home),
    path("", lambda request: HttpResponse("Novels Home")),
    path('<int:novel_id>/', views.novel_detail, name='novel_detail'),
]
