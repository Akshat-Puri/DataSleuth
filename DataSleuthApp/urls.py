from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('file_success/', views.file_success, name='file_success'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),  # built-in view Login page
    path('login/', views.custom_login_view, name='login'),  # custom login page
    path('logs/', views.logging, name='logging'),  # path for viewing logs
    path('delete_logs/', views.delete_logs, name='delete_logs'),
    path('custom_logout/', views.custom_logout, name='custom_logout'),
]
