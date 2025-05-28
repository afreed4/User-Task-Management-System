from django.urls import path
from . import views

urlpatterns = [
    path("", views.super_admin_login, name="super_admin_login"),
    path("staff_view/", views.list_staff, name="staff_view"),
    path("edit_staff/<int:user_id>/", views.edit_staff, name="edit_staff"),
    path("view_user/<int:user_id>/", views.view_staff, name="view_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("get-districts/", views.get_districts, name="get_districts"),
    path("get_users_of_each_admin/",views.get_users_of_each_admin,name='get_users_of_each_admin'),
    
    path("create_admin/", views.create_admin, name="create_admin"),
    path("manage_admin/", views.manage_admin, name="manage_admin"),
    path(
        "promote_to_admin/<int:user_id>/",
        views.promote_to_admin,
        name="promote_to_admin",
    ),
    path(
        "demote_from_user/<int:user_id>/",
        views.demote_from_admin,
        name="demote_from_user",
    ),
    path("create_user/", views.create_user, name="create_user"),
    path("manage_users/", views.manage_users, name="manage_users"),
    
    path('manage_tasks/', views.fetch_all_task, name='manage_tasks'),
    path('view_task_details/<int:task_id>/',views.view_task_details,name='view_task_details'),
    path('edit_task/<int:task_id>/',views.edit_task,name='edit_task'),
    path('super_create_task/',views.create_task,name='super_create_task'),
    path('delete_task/',views.delete_task,name='delete_task'),
    path('fetch_completed_task/',views.fetch_completed_task,name='fetch_completed_task'),
    
    path("log_out/", views.logout_user, name="log_out"),
]
