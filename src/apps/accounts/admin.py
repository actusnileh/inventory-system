from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from .models import Department, User



@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("created_at",)
    ordering = ("name",)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "department")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "username",
        "get_full_name",
        "email",
        "role",
        "department",
        "job_title",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    autocomplete_fields = ("department", "groups", "user_permissions")
    readonly_fields = ("last_login", "date_joined", "last_activity")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Персональные данные"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "department",
                    "job_title",
                    "role",
                    "avatar",
                    "phone",
                    "timezone",
                    "bio",
                )
            },
        ),
        (
            _("Права"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Важные даты"), {"fields": ("last_login", "date_joined", "last_activity")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "department",
                    "job_title",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    def get_full_name(self, obj: User) -> str:
        return obj.get_display_name()

    get_full_name.short_description = "ФИО"  # type: ignore[attr-defined]


admin.site.register(Department, DepartmentAdmin)
