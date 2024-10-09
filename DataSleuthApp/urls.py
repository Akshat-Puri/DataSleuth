from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('file_success/', views.file_success, name='file_success'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),  # built-in view Login page
    path('login/', views.custom_login_view, name='login'),  # custom login page
    path('logs/', views.log_list, name='log_list'),  # path for viewing logs
]
