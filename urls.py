from django.urls import path
from . import views

urlpatterns = [
    path('csrf-token', views.get_csrf_token, name='csrf-token'),
    path('auth/register', views.register_view, name='register'),
    path('auth/login', views.login_view, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('tasks', views.task_list_create_view, name='task-list'),
    path('tasks/<int:pk>', views.task_detail_view, name='task-detail'),
]