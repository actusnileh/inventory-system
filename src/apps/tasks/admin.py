from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Project,
    Task,
    TaskActivity,
    TaskAttachment,
    TaskAssignment,
    TaskChecklistItem,
    TaskComment,
    TaskDependency,
)


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 0
    autocomplete_fields = ("assignee", "assigned_by")
    fields = ("assignee", "assigned_by", "assigned_at", "workload")
    readonly_fields = ("assigned_at",)


class TaskChecklistInline(admin.TabularInline):
    model = TaskChecklistItem
    extra = 1
    fields = ("title", "is_completed", "order", "completed_at")
    readonly_fields = ("completed_at",)


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    fields = ("title", "file", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)
    autocomplete_fields = ("uploaded_by",)


class TaskCommentInline(admin.StackedInline):
    model = TaskComment
    extra = 0
    fields = ("author", "message", "is_internal", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("author",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "status",
        "priority",
        "assignee",
        "due_date",
        "is_archived",
    )
    list_filter = (
        "status",
        "priority",
        "project",
        "is_archived",
        "due_date",
    )
    search_fields = ("title", "description", "project__name")
    autocomplete_fields = ("project", "created_by", "assignee")
    filter_horizontal = ("watchers", "assets")
    inlines = (TaskAssignmentInline, TaskChecklistInline, TaskAttachmentInline, TaskCommentInline)
    readonly_fields = ("created_at", "updated_at", "completed_at")
    date_hierarchy = "due_date"
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("project", "title", "description", "status", "priority", "is_archived")}),
        (_("Сроки"), {"fields": ("start_date", "due_date", "completed_at")}),
        (_("Команда"), {"fields": ("created_by", "assignee", "watchers")}),
        (_("Инвентарь"), {"fields": ("assets",)}),
        (_("Системные поля"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "owner", "is_active", "start_date", "due_date")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    prepopulated_fields = {"code": ("name",)}
    filter_horizontal = ("members",)
    autocomplete_fields = ("owner",)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "is_internal", "created_at")
    list_filter = ("is_internal", "created_at")
    search_fields = ("task__title", "message")
    autocomplete_fields = ("task", "author")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("task", "title", "uploaded_by", "uploaded_at")
    search_fields = ("task__title", "title")
    autocomplete_fields = ("task", "uploaded_by")
    readonly_fields = ("uploaded_at",)


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("blocking", "blocked", "created_at")
    search_fields = ("blocking__title", "blocked__title")
    autocomplete_fields = ("blocking", "blocked")


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ("task", "action", "author", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("task__title",)
    autocomplete_fields = ("task", "author")
    readonly_fields = ("created_at",)


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ("task", "assignee", "assigned_by", "assigned_at", "workload")
    search_fields = ("task__title", "assignee__username")
    autocomplete_fields = ("task", "assignee", "assigned_by")
    readonly_fields = ("assigned_at",)


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("task", "title", "is_completed", "order")
    list_filter = ("is_completed",)
    search_fields = ("task__title", "title")
    autocomplete_fields = ("task",)


admin.site.site_title = "Управление задачами и инвентарем"
admin.site.site_header = "Администрирование системы"
