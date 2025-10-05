from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    name = models.CharField("Название", max_length=160)
    code = models.SlugField("Код", max_length=32, unique=True)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        User,
        verbose_name="Владелец",
        related_name="owned_projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    members = models.ManyToManyField(User, verbose_name="Команда", blank=True, related_name="projects")
    is_active = models.BooleanField("Активен", default=True)
    start_date = models.DateField("Старт", null=True, blank=True)
    due_date = models.DateField("Дедлайн", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.code:
            self.code = slugify(self.name)[:32]
        super().save(*args, **kwargs)


class TaskTag(models.Model):
    name = models.CharField("Тег", max_length=60, unique=True)
    color = models.CharField("Цвет", max_length=12, default="#6366f1")

    class Meta:
        verbose_name = "Тег задачи"
        verbose_name_plural = "Теги задач"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Бэклог"
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        REVIEW = "review", "На проверке"
        BLOCKED = "blocked", "Заблокировано"
        DONE = "done", "Завершено"

    class Priority(models.IntegerChoices):
        LOW = 10, "Низкий"
        NORMAL = 20, "Средний"
        HIGH = 30, "Высокий"
        CRITICAL = 40, "Критический"

    project = models.ForeignKey(
        Project,
        verbose_name="Проект",
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.BACKLOG)
    priority = models.PositiveSmallIntegerField(
        "Приоритет", choices=Priority.choices, default=Priority.NORMAL
    )
    created_by = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="created_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assignee = models.ForeignKey(
        User,
        verbose_name="Исполнитель",
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    watchers = models.ManyToManyField(User, verbose_name="Наблюдатели", related_name="watched_tasks", blank=True)
    assets = models.ManyToManyField("inventory.Asset", verbose_name="Оборудование", related_name="tasks", blank=True)
    tags = models.ManyToManyField(TaskTag, verbose_name="Теги", blank=True, related_name="tasks")
    start_date = models.DateField("Старт", null=True, blank=True)
    due_date = models.DateField("Дедлайн", null=True, blank=True)
    completed_at = models.DateTimeField("Завершено", null=True, blank=True)
    estimated_hours = models.DecimalField("Оценка, ч", max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField("Затраты, ч", max_digits=6, decimal_places=2, null=True, blank=True)
    progress = models.PositiveSmallIntegerField("Прогресс, %", default=0)
    is_archived = models.BooleanField("Архив", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("status", "priority"))]

    def __str__(self) -> str:
        return self.title

    def set_status(self, status: str, *, user: User | None = None) -> None:
        self.status = status
        if status == self.Status.DONE and not self.completed_at:
            self.completed_at = timezone.now()
        self.save()
        TaskActivity.objects.create(
            task=self,
            author=user,
            action=TaskActivity.Action.STATUS,
            payload={"status": status},
        )

    def mark_progress(self, value: int, *, user: User | None = None) -> None:
        self.progress = max(0, min(100, value))
        self.save(update_fields=["progress"])
        TaskActivity.objects.create(
            task=self,
            author=user,
            action=TaskActivity.Action.PROGRESS,
            payload={"progress": self.progress},
        )


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задача", related_name="assignments", on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, verbose_name="Исполнитель", related_name="task_assignments", on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        User,
        verbose_name="Назначил",
        related_name="assigned_by_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assigned_at = models.DateTimeField("Назначено", default=timezone.now)
    workload = models.DecimalField("Нагрузка, ч", max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"
        unique_together = ("task", "assignee")

    def __str__(self) -> str:
        return f"{self.task} → {self.assignee}"


class TaskChecklistItem(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задача", related_name="checklist", on_delete=models.CASCADE)
    title = models.CharField("Шаг", max_length=200)
    is_completed = models.BooleanField("Выполнено", default=False)
    completed_at = models.DateTimeField("Выполнено в", null=True, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Шаг чек-листа"
        verbose_name_plural = "Чек-лист"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return self.title

    def mark_done(self, *, user: User | None = None) -> None:
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=["is_completed", "completed_at"])
            TaskActivity.objects.create(
                task=self.task,
                author=user,
                action=TaskActivity.Action.CHECKLIST,
                payload={"item": self.pk, "title": self.title},
            )


class TaskComment(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задача", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name="Автор", related_name="task_comments", on_delete=models.SET_NULL, null=True)
    message = models.TextField("Комментарий")
    is_internal = models.BooleanField("Видно только сотрудникам", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"Комментарий к {self.task}"


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задача", related_name="attachments", on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, verbose_name="Автор", on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField("Файл", upload_to="tasks/attachments/")
    title = models.CharField("Название", max_length=160, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Файл задачи"
        verbose_name_plural = "Файлы задач"

    def __str__(self) -> str:
        return self.title or self.file.name


class TaskDependency(models.Model):
    blocking = models.ForeignKey(
        Task,
        verbose_name="Блокирующая задача",
        related_name="dependent_tasks",
        on_delete=models.CASCADE,
    )
    blocked = models.ForeignKey(
        Task,
        verbose_name="Зависимая задача",
        related_name="dependencies",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Зависимость"
        verbose_name_plural = "Зависимости"
        unique_together = ("blocking", "blocked")

    def __str__(self) -> str:
        return f"{self.blocking} → {self.blocked}"


class TaskActivity(models.Model):
    class Action(models.TextChoices):
        STATUS = "status", "Статус"
        PROGRESS = "progress", "Прогресс"
        COMMENT = "comment", "Комментарий"
        CHECKLIST = "checklist", "Чек-лист"
        ATTACHMENT = "attachment", "Файл"

    task = models.ForeignKey(Task, verbose_name="Задача", related_name="activity", on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="logged_task_activity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField("Тип", max_length=32, choices=Action.choices)
    payload = models.JSONField("Данные", default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активность"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.get_action_display()} для {self.task}"


# signals to log comments & attachments as activity
from django.db.models.signals import post_save  # noqa  E402  pylint: disable=wrong-import-position
from django.dispatch import receiver  # noqa  E402  pylint: disable=wrong-import-position


@receiver(post_save, sender=TaskComment)
def log_comment_activity(sender, instance: TaskComment, created: bool, **kwargs) -> None:  # pragma: no cover
    if created:
        TaskActivity.objects.create(
            task=instance.task,
            author=instance.author,
            action=TaskActivity.Action.COMMENT,
            payload={"comment": instance.pk},
        )


@receiver(post_save, sender=TaskAttachment)
def log_attachment_activity(sender, instance: TaskAttachment, created: bool, **kwargs) -> None:  # pragma: no cover
    if created:
        TaskActivity.objects.create(
            task=instance.task,
            author=instance.uploaded_by,
            action=TaskActivity.Action.ATTACHMENT,
            payload={"attachment": instance.pk},
        )
