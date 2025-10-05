from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Project, Task, TaskActivity, TaskComment


class TaskBoardViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="executor",
            email="executor@example.com",
            password="task-pass",
        )
        self.project = Project.objects.create(name="Новый проект", code="new-project", owner=self.user)
        self.task = Task.objects.create(
            project=self.project,
            title="Настроить оборудование",
            created_by=self.user,
            assignee=self.user,
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.HIGH,
            progress=60,
        )
        self.todo_task = Task.objects.create(
            project=self.project,
            title="Собрать требования",
            created_by=self.user,
            status=Task.Status.TODO,
        )
        TaskActivity.objects.create(task=self.task, author=self.user, action=TaskActivity.Action.STATUS, payload={"status": Task.Status.IN_PROGRESS})
        TaskComment.objects.create(task=self.task, author=self.user, message="Проверить сроки")

    def test_task_board_response_ok(self):
        response = self.client.get(reverse("tasks:board"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_board.html")

    def test_board_columns_contain_tasks(self):
        response = self.client.get(reverse("tasks:board"))
        board_columns = response.context["board_columns"]
        self.assertIn("in_progress", board_columns)
        self.assertIn(self.task, list(board_columns["in_progress"]["items"]))

    def test_recent_activity_and_comments(self):
        response = self.client.get(reverse("tasks:board"))
        self.assertIn(self.task, [activity.task for activity in response.context["recent_activity"]])
        self.assertIn(self.task, [comment.task for comment in response.context["recent_comments"]])
