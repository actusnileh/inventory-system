from django.urls import path

from .views import TaskBoardView

app_name = "tasks"

urlpatterns = [
    path("", TaskBoardView.as_view(), name="board"),
]
