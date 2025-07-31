from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'novels'

urlpatterns = [
    path("", views.Home),
    path('<slug:novel_slug>/', views.novel_detail, name='novel_detail'),
    path('novel/<slug:novel_slug>/chapter/<slug:chapter_slug>/', 
         views.chapter_detail_view, 
         name='chapter_detail'),
    path('ajax/load-chunks/<int:chapter_id>/', 
         views.load_more_chunks, 
         name='load_more_chunks'),
    
    path('ajax/save-progress/', 
         views.save_reading_progress, 
         name='save_reading_progress'),
    
    # Chapter list for a novel
    path('novel/<slug:novel_slug>/chapters/', 
         views.chapter_list_view, 
         name='chapter_list'),
]
