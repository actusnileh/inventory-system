# Generated manually for task tracking models
from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="Название")),
                ("code", models.SlugField(max_length=32, unique=True, verbose_name="Код")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("start_date", models.DateField(blank=True, null=True, verbose_name="Старт")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Дедлайн")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "members",
                    models.ManyToManyField(blank=True, related_name="projects", to=settings.AUTH_USER_MODEL, verbose_name="Команда"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_projects",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Проект",
                "verbose_name_plural": "Проекты",
            },
        ),
        migrations.CreateModel(
            name="TaskTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=60, unique=True, verbose_name="Тег")),
                ("color", models.CharField(default="#6366f1", max_length=12, verbose_name="Цвет")),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Тег задачи",
                "verbose_name_plural": "Теги задач",
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("backlog", "Бэклог"),
                            ("todo", "К выполнению"),
                            ("in_progress", "В работе"),
                            ("review", "На проверке"),
                            ("blocked", "Заблокировано"),
                            ("done", "Завершено"),
                        ],
                        default="backlog",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        choices=[(10, "Низкий"), (20, "Средний"), (30, "Высокий"), (40, "Критический")],
                        default=20,
                        verbose_name="Приоритет",
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True, verbose_name="Старт")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Дедлайн")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Завершено")),
                ("estimated_hours", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="Оценка, ч")),
                ("actual_hours", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="Затраты, ч")),
                ("progress", models.PositiveSmallIntegerField(default=0, verbose_name="Прогресс, %")),
                ("is_archived", models.BooleanField(default=False, verbose_name="Архив")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Исполнитель",
                    ),
                ),
                (
                    "assets",
                    models.ManyToManyField(blank=True, related_name="tasks", to="inventory.asset", verbose_name="Оборудование"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to="tasks.project", verbose_name="Проект"),
                ),
                (
                    "tags",
                    models.ManyToManyField(blank=True, related_name="tasks", to="tasks.tasktag", verbose_name="Теги"),
                ),
                (
                    "watchers",
                    models.ManyToManyField(blank=True, related_name="watched_tasks", to=settings.AUTH_USER_MODEL, verbose_name="Наблюдатели"),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Задача",
                "verbose_name_plural": "Задачи",
                "indexes": [models.Index(fields=["status", "priority"])],
            },
        ),
        migrations.CreateModel(
            name="TaskAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assigned_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Назначено")),
                ("workload", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="Нагрузка, ч")),
                (
                    "assigned_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_by_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Назначил",
                    ),
                ),
                (
                    "assignee",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="task_assignments", to=settings.AUTH_USER_MODEL, verbose_name="Исполнитель"),
                ),
                (
                    "task",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="tasks.task", verbose_name="Задача"),
                ),
            ],
            options={
                "verbose_name": "Назначение",
                "verbose_name_plural": "Назначения",
                "unique_together": {("task", "assignee")},
            },
        ),
        migrations.CreateModel(
            name="TaskChecklistItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Шаг")),
                ("is_completed", models.BooleanField(default=False, verbose_name="Выполнено")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Выполнено в")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                (
                    "task",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="checklist", to="tasks.task", verbose_name="Задача"),
                ),
            ],
            options={
                "ordering": ("order", "id"),
                "verbose_name": "Шаг чек-листа",
                "verbose_name_plural": "Чек-лист",
            },
        ),
        migrations.CreateModel(
            name="TaskComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(verbose_name="Комментарий")),
                ("is_internal", models.BooleanField(default=False, verbose_name="Видно только сотрудникам")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="task_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="tasks.task", verbose_name="Задача"),
                ),
            ],
            options={
                "ordering": ("created_at",),
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.CreateModel(
            name="TaskAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="tasks/attachments/", verbose_name="Файл")),
                ("title", models.CharField(blank=True, max_length=160, verbose_name="Название")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "task",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="tasks.task", verbose_name="Задача"),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "Файл задачи",
                "verbose_name_plural": "Файлы задач",
            },
        ),
        migrations.CreateModel(
            name="TaskDependency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "blocked",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dependencies", to="tasks.task", verbose_name="Зависимая задача"),
                ),
                (
                    "blocking",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dependent_tasks", to="tasks.task", verbose_name="Блокирующая задача"),
                ),
            ],
            options={
                "verbose_name": "Зависимость",
                "verbose_name_plural": "Зависимости",
                "unique_together": {("blocking", "blocked")},
            },
        ),
        migrations.CreateModel(
            name="TaskActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("status", "Статус"),
                            ("progress", "Прогресс"),
                            ("comment", "Комментарий"),
                            ("checklist", "Чек-лист"),
                            ("attachment", "Файл"),
                        ],
                        max_length=32,
                        verbose_name="Тип",
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict, verbose_name="Данные")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="logged_task_activity",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activity", to="tasks.task", verbose_name="Задача"),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Активность",
                "verbose_name_plural": "Активность",
            },
        ),
    ]
