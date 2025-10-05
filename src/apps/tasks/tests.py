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
        self.client.force_login(self.user)
        response = self.client.get(reverse("tasks:board"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_board.html")

    def test_board_columns_contain_tasks(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tasks:board"))
        board_columns = response.context["board_columns"]
        self.assertIn("in_progress", board_columns)
        self.assertIn(self.task, list(board_columns["in_progress"]["items"]))

    def test_recent_activity_and_comments(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tasks:board"))
        self.assertIn(self.task, [activity.task for activity in response.context["recent_activity"]])
        self.assertIn(self.task, [comment.task for comment in response.context["recent_comments"]])

    def test_create_view_creates_task(self):
        self.client.force_login(self.user)
        payload = {
            "project": self.project.pk,
            "title": "Новая",
            "description": "Описание",
            "status": Task.Status.TODO,
            "priority": Task.Priority.NORMAL,
            "assignee": self.user.pk,
            "watchers": [self.user.pk],
            "assets": [],
            "start_date": "",
            "due_date": "",
        }
        response = self.client.post(reverse("tasks:task_create"), payload)
        self.assertRedirects(response, reverse("tasks:board"))
        self.assertTrue(Task.objects.filter(title="Новая").exists())

    def test_project_create_requires_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tasks:project_create"))
        self.assertEqual(response.status_code, 403)

        admin = get_user_model().objects.create_user(
            username="admin2",
            email="admin2@example.com",
            password="task-pass",
        )
        admin.promote_to_admin()
        self.client.force_login(admin)
        response = self.client.post(
            reverse("tasks:project_create"),
            {
                "name": "Проект",
                "code": "proj-1",
                "description": "",
                "members": [self.user.pk],
                "is_active": True,
                "start_date": "",
                "due_date": "",
            },
        )
        self.assertRedirects(response, reverse("tasks:board"))
        project = Project.objects.get(code="proj-1")
        self.assertIn(admin, project.members.all())
