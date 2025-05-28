

from django.urls import path
from . import views

urlpatterns = [
    path('fetch_task/',views.FetchAllTask.as_view(),name='fetch_task'),
    path('update_task_response/',views.UpdateTaskResponse.as_view(),name='update_task_response'),
]