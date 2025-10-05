from collections import OrderedDict
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from src.apps.accounts.mixins import AdminRequiredMixin

from .forms import ProjectForm, TaskForm
from .models import Project, Task, TaskActivity, TaskComment


class TaskBoardView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/task_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = (
            Task.objects.select_related("project", "assignee", "created_by")
            .prefetch_related("watchers", "assets")
            .order_by("priority", "due_date")
        )

        board_columns = OrderedDict()
        for status_key, status_label in Task.Status.choices:
            board_columns[status_key] = {
                "label": status_label,
                "items": tasks.filter(status=status_key)[:15],
            }

        priority_data = []
        for item in tasks.values("priority").annotate(total=Count("id")).order_by("-total"):
            try:
                label = Task.Priority(item["priority"]).label
            except ValueError:
                label = item["priority"]
            priority_data.append({"priority": item["priority"], "label": label, "total": item["total"]})

        context.update(
            {
                "board_columns": board_columns,
                "project_count": Project.objects.filter(is_active=True).count(),
                "task_total": tasks.count(),
                "tasks_completed": tasks.filter(status=Task.Status.DONE).count(),
                "recent_activity": TaskActivity.objects.select_related("task", "author")
                .order_by("-created_at")[:10],
                "recent_comments": TaskComment.objects.select_related("task", "author")
                .order_by("-created_at")[:5],
                "priority_breakdown": priority_data,
                "can_create_task": self.request.user.is_authenticated,
                "can_create_project": getattr(self.request.user, "is_admin_role", False),
            }
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:board")
    extra_context = {"task": None}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Задача создана")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:board")
    context_object_name = "task"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Задача обновлена")
        return super().form_valid(form)


class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "tasks/project_form.html"
    success_url = reverse_lazy("tasks:board")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        if self.request.user not in self.object.members.all():
            self.object.members.add(self.request.user)
        messages.success(self.request, "Проект создан")
        return response


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest("Invalid payload")

        status = payload.get("status")
        if status not in Task.Status.values:
            return HttpResponseBadRequest("Unsupported status")

        task = Task.objects.select_related("project").filter(pk=pk).first()
        if task is None:
            return HttpResponseBadRequest("Task not found")

        if not request.user.is_admin_role:
            is_project_member = task.project.members.filter(pk=request.user.pk).exists()
            is_assignee = task.assignee_id == request.user.id
            is_creator = task.created_by_id == request.user.id
            is_watcher = task.watchers.filter(pk=request.user.pk).exists()
            if not (is_project_member or is_assignee or is_creator or is_watcher):
                return HttpResponseBadRequest("Forbidden")

        task.set_status(status, user=request.user)
        return JsonResponse({"status": task.get_status_display()})
