from collections import OrderedDict

from django.db.models import Count
from django.views.generic import TemplateView

from .models import Project, Task, TaskActivity, TaskComment


class TaskBoardView(TemplateView):
    template_name = "tasks/task_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = (
            Task.objects.select_related("project", "assignee", "created_by")
            .prefetch_related("tags", "watchers", "assets")
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
            }
        )
        return context
