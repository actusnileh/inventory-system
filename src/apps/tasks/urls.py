from django.urls import path

from .views import ProjectCreateView, TaskBoardView, TaskCreateView, TaskUpdateView

app_name = "tasks"

urlpatterns = [
    path("", TaskBoardView.as_view(), name="board"),
    path("tasks/add/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task_update"),
    path("projects/add/", ProjectCreateView.as_view(), name="project_create"),
]
