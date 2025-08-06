from django.urls import path
from django.http import HttpResponse
from . import views
from . import views_admin

app_name = 'novels'

urlpatterns = [
    path("", views.Home, name = "home"),
    path("admin/", views.Admin, name="admin"),
    path("create/", views.NovelCreateView.as_view(), name="novel_create"),
    path("admin/dashboard/", views.Dashboard, name="dashboard"),
    path("admin/users/", views.Users, name="users"),
    path("admin/novels/", views.Novels, name="novels"),
    path("admin/requests/", views.Requests, name="requests"),
    path("most-read-novels/", views.most_read_novels, name ="most-read-novels"),
    path("finish-novels/", views.finish_novels, name ="finish-novels"),
    path("new-novels/", views.new_novels, name ="new-novels"),
    path("admin/comments/", views.Comments, name="comments"),
    path("my-novels/", views.MyNovelsView.as_view(), name="my_novels"),
    
    # Specific routes must come before generic slug patterns
    path('chapter-upload-rules/', 
         views.chapter_upload_rules, 
         name='chapter_upload_rules'),
    
    path('ajax/load-chunks/<int:chapter_id>/', 
         views.load_more_chunks, 
         name='load_more_chunks'),
    
    path('ajax/save-progress/', 
         views.save_reading_progress, 
         name='save_reading_progress'),
    
    # Chapter and novel routes with specific prefixes
    path('novel/<slug:novel_slug>/chapter/<slug:chapter_slug>/', 
         views.chapter_detail_view, 
         name='chapter_detail'),
    
    path('novel/<slug:novel_slug>/chapters/', 
         views.chapter_list_view, 
         name='chapter_list'),
    
    # Admin routes
    path('admin/', 
         views_admin.admin_dashboard, name='admin_dashboard'),

    path('admin/tags/', 
         views_admin.admin_tag_list, 
         name='admin_tag_list'),

    path('admin/tags/create/', 
         views_admin.admin_tag_create, 
         name='admin_tag_create'),

    path('admin/tags/<slug:tag_slug>/edit/', 
         views_admin.admin_tag_update, 
         name='admin_tag_update'),

     path('admin/tags/<slug:tag_slug>/delete/', 
          views_admin.admin_tag_delete, 
          name='admin_tag_delete'),
     
     path("admin/requests/novel/<slug:slug>/", 
          views_admin.novel_request_detail, 
          name="novel_request_detail"),

     path("admin/requests/novel/<slug:slug>/approve/", 
          views_admin.admin_approve_novel, 
          name="admin_approve_novel"),
     
     path("admin/requests/novel/<slug:slug>/reject/", 
          views_admin.admin_reject_novel, 
          name="admin_reject_novel"),
     
     path('admin/requests/chapter/<slug:chapter_slug>/',
          views_admin.chapter_review,
          name='chapter_review'),

     path('admin/authors/', 
          views_admin.author_list, 
          name='author_list'),

     path('admin/authors/create/', 
          views_admin.author_create, 
          name='author_create'),

     path('admin/authors/<int:pk>/update/', 
          views_admin.author_update, 
          name='author_update'),

     path('admin/authors/<int:pk>/delete/', 
          views_admin.author_delete, 
          name='author_delete'),

     path('admin/artists/', 
          views_admin.artist_list, 
          name='artist_list'),

     path('admin/artists/create/', 
          views_admin.artist_create, 
          name='artist_create'),

     path('admin/artists/<int:pk>/update/', 
          views_admin.artist_update, 
          name='artist_update'),

     path('admin/artists/<int:pk>/delete/', 
          views_admin.artist_delete, 
          name='artist_delete'),
     
     path('admin/requests/chapter/<slug:chapter_slug>/approve/',
          views_admin.approve_chapter_view,
          name='approve_chapter'),
     
     path('admin/requests/chapter/<slug:chapter_slug>/reject/',
          views_admin.reject_chapter_view,
          name='reject_chapter'),
    
    # Generic novel slug patterns - must come last
    path('<slug:novel_slug>/', views.novel_detail, name='novel_detail'),
    path('<slug:novel_slug>/add-chapter/', views.chapter_add_view, name='chapter_add'),
]
