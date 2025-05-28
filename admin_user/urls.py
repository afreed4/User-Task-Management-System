
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.view_users, name='admin_dashboard'),
    path('fill_user_name/', views.fill_user_name, name='fill_user_name'),
    path('create_task/',views.create_task, name='create_task'),
    path('view_task/', views.view_task, name='view_task'),
    path('task_details/<int:task_id>/', views.task_details, name='task_details'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('fill_user_list_withdata/<int:task_id>/', views.fill_user_list_withdata, name='fill_user_list_withdata'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('admin_fetch_completed_task/',views.admin_fetch_completed_task,name='admin_fetch_completed_task')
]