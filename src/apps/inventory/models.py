from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class AssetCategory(models.Model):
    """Категории оборудования."""

    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Код", max_length=150, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="Родительская категория",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Location(models.Model):
    name = models.CharField("Локация", max_length=160)
    code = models.CharField("Код", max_length=32, unique=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    description = models.TextField("Комментарий", blank=True)
    contact = models.ForeignKey(
        User,
        verbose_name="Контакт",
        null=True,
        blank=True,
        related_name="managed_locations",
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Vendor(models.Model):
    name = models.CharField("Поставщик", max_length=150)
    website = models.URLField("Сайт", blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    notes = models.TextField("Заметки", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AssetTag(models.Model):
    name = models.CharField("Тег", max_length=60, unique=True)
    color = models.CharField("Цвет", max_length=12, default="#0ea5e9")

    class Meta:
        verbose_name = "Тег оборудования"
        verbose_name_plural = "Теги оборудования"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Asset(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "В наличии"
        IN_USE = "in_use", "Выдано"
        RESERVED = "reserved", "Зарезервировано"
        MAINTENANCE = "maintenance", "Обслуживание"
        LOST = "lost", "Утеряно"
        RETIRED = "retired", "Списано"

    class Condition(models.TextChoices):
        NEW = "new", "Новый"
        GOOD = "good", "Отличное"
        NORMAL = "normal", "Хорошее"
        NEEDS_REPAIR = "needs_repair", "Требует ремонта"
        BROKEN = "broken", "Неисправно"

    name = models.CharField("Название", max_length=160)
    category = models.ForeignKey(
        AssetCategory,
        verbose_name="Категория",
        related_name="assets",
        on_delete=models.PROTECT,
    )
    inventory_code = models.CharField("Инвентарный номер", max_length=64, unique=True)
    serial_number = models.CharField("Серийный номер", max_length=128, blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    condition = models.CharField("Состояние", max_length=20, choices=Condition.choices, default=Condition.NEW)
    location = models.ForeignKey(
        Location,
        verbose_name="Локация",
        related_name="assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    custodian = models.ForeignKey(
        User,
        verbose_name="Ответственный",
        related_name="custodian_assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        User,
        verbose_name="Выдан пользователю",
        related_name="assigned_assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(AssetTag, verbose_name="Теги", blank=True, related_name="assets")
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Поставщик",
        related_name="assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    purchase_date = models.DateField("Дата закупки", null=True, blank=True)
    purchase_price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiration = models.DateField("Гарантия до", null=True, blank=True)
    specs = models.JSONField("Характеристики", blank=True, default=dict)
    notes = models.TextField("Заметки", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ("name", "inventory_code")

    def __str__(self) -> str:
        return f"{self.name} ({self.inventory_code})"

    def mark_status(self, status: str, *, by: User | None = None, note: str | None = None) -> None:
        previous_status = self.status
        self.status = status
        self.save(update_fields=["status"])
        AssetLogEntry.objects.create(
            asset=self,
            action=AssetLogEntry.Action.STATUS_CHANGE,
            performed_by=by,
            from_status=previous_status,
            to_status=status,
            notes=note or "",
        )


class AssetAttachment(models.Model):
    asset = models.ForeignKey(Asset, verbose_name="Оборудование", related_name="attachments", on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=160, blank=True)
    file = models.FileField("Файл", upload_to="assets/attachments/", blank=True, null=True)
    uploaded_at = models.DateTimeField("Загружено", auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        verbose_name="Загрузил",
        related_name="asset_attachments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Файл оборудования"
        verbose_name_plural = "Файлы оборудования"

    def __str__(self) -> str:
        return self.title or f"Файл #{self.pk}"


class AssetLogEntry(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Создание"
        UPDATED = "updated", "Изменение"
        STATUS_CHANGE = "status_change", "Смена статуса"
        ASSIGNED = "assigned", "Выдача"
        RETURNED = "returned", "Возврат"
        MAINTENANCE = "maintenance", "Обслуживание"
        NOTE = "note", "Комментарий"

    asset = models.ForeignKey(Asset, verbose_name="Оборудование", related_name="log_entries", on_delete=models.CASCADE)
    action = models.CharField("Действие", max_length=32, choices=Action.choices)
    performed_by = models.ForeignKey(
        User,
        verbose_name="Ответственный",
        related_name="asset_logs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    from_status = models.CharField("Статус до", max_length=20, blank=True)
    to_status = models.CharField("Статус после", max_length=20, blank=True)
    notes = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Время", default=timezone.now)

    class Meta:
        verbose_name = "Журнал операции"
        verbose_name_plural = "Журнал операций"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.get_action_display()} — {self.asset}"


class MaintenanceRecord(models.Model):
    class Kind(models.TextChoices):
        SERVICE = "service", "Плановое обслуживание"
        REPAIR = "repair", "Ремонт"
        UPDATE = "update", "Обновление ПО"
        INSPECTION = "inspection", "Осмотр"

    class Status(models.TextChoices):
        PLANNED = "planned", "Запланировано"
        IN_PROGRESS = "in_progress", "В процессе"
        DONE = "done", "Завершено"
        CANCELED = "canceled", "Отменено"

    asset = models.ForeignKey(Asset, verbose_name="Оборудование", related_name="maintenance", on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=160)
    kind = models.CharField("Тип", max_length=20, choices=Kind.choices, default=Kind.SERVICE)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.PLANNED)
    scheduled_for = models.DateField("Запланировано на", null=True, blank=True)
    completed_at = models.DateField("Завершено", null=True, blank=True)
    description = models.TextField("Описание работ", blank=True)
    cost = models.DecimalField("Стоимость", max_digits=9, decimal_places=2, null=True, blank=True)
    responsible = models.ForeignKey(
        User,
        verbose_name="Ответственный",
        related_name="maintenance_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    contractor = models.ForeignKey(
        Vendor,
        verbose_name="Подрядчик",
        related_name="maintenance_records",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Обслуживание"
        verbose_name_plural = "Обслуживание"
        ordering = ("-scheduled_for", "-created_at")

    def __str__(self) -> str:
        return f"{self.title} — {self.asset}"

    @property
    def is_overdue(self) -> bool:
        return bool(self.scheduled_for and self.status != self.Status.DONE and self.scheduled_for < timezone.now().date())
