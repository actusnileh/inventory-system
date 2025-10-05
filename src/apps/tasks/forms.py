from django import forms
from django.contrib.auth import get_user_model

from .models import Project, Task, TaskTag

User = get_user_model()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "code", "description", "members", "is_active", "start_date", "due_date")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = User.objects.order_by("username")
        if owner:
            self.instance.owner = owner
            self.initial.setdefault("members", [owner.pk])
        for name, field in self.fields.items():
            if name == "is_active":
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault("class", "form-select")
                field.widget.attrs.setdefault("multiple", "multiple")
            elif isinstance(field.widget, forms.Textarea):
                continue
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "watchers",
            "assets",
            "tags",
            "start_date",
            "due_date",
            "estimated_hours",
            "actual_hours",
            "progress",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(is_active=True).order_by("name")
        self.fields["assignee"].queryset = User.objects.order_by("username")
        self.fields["watchers"].queryset = User.objects.order_by("username")
        self.fields["tags"].queryset = TaskTag.objects.order_by("name")
        self.fields["watchers"].required = False
        self.fields["assets"].required = False
        self.fields["tags"].required = False
        if user and not user.is_admin_role:
            self.fields["project"].queryset = self.fields["project"].queryset.filter(members=user)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault("class", "form-select")
                field.widget.attrs.setdefault("multiple", "multiple")
            elif isinstance(field.widget, forms.Textarea):
                continue
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")
