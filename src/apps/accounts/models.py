from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Department(models.Model):
    """Организационная единица компании."""

    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Код", max_length=150, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    color = models.CharField("Цвет", max_length=12, default="#4f46e5")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username: str, email: str | None = None, password: str | None = None, **extra_fields):
        extra_fields.setdefault("role", self.model.Role.USER)
        if not username:
            raise ValueError("Пользователь должен иметь имя пользователя")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str | None = None, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", self.model.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с ролями и расширенными полями."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        USER = "user", "Пользователь"

    department = models.ForeignKey(
        Department,
        verbose_name="Отдел",
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    role = models.CharField("Роль", max_length=20, choices=Role.choices, default=Role.USER)
    job_title = models.CharField("Должность", max_length=120, blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^[0-9\-\+\(\)\s]+$", message="Используйте допустимый формат номера")],
    )
    user_timezone = models.CharField("Часовой пояс", max_length=64, default="Europe/Moscow")
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    bio = models.TextField("О себе", blank=True)
    last_activity = models.DateTimeField("Последняя активность", default=timezone.now)

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.get_display_name()

    def touch_activity(self) -> None:
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    def get_display_name(self) -> str:
        full_name = self.get_full_name().strip()
        return full_name or self.username

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN

    def promote_to_admin(self) -> None:
        self.role = self.Role.ADMIN
        self.is_staff = True
        self.is_superuser = True
        self.save(update_fields=["role", "is_staff", "is_superuser"])
