# errands/urls.py
from django.urls import path
from . import views
from .views import (
    LoginView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TakeTaskView,
    TaskStatusUpdateView,
    TaskReviewView,
    NotificationListView,
    login_view, 
    logout_view, 
    index_view,
    register_view,
    take_tasks_view,
    ajax_take_task_view,
    profile_view,
)

urlpatterns = [
    path('', views.main_page, name='main'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/take/', TakeTaskView.as_view(), name='task-take'),
    path('tasks/<int:pk>/status/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('tasks/<int:pk>/review/', TaskReviewView.as_view(), name='task-review'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('login_page/', login_view, name='login_page'),
    path('logout_page/', logout_view, name='logout_page'),
    path('index/', index_view, name='index'),
    path('register_page/', register_view, name='register_page'),
    path('take_tasks/', take_tasks_view, name='take_tasks'),
    path('ajax_take_task/<int:task_id>/', ajax_take_task_view, name='ajax_take_task'),
    path('profile/', profile_view, name='profile'),
]
