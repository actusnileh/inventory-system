# Generated manually for inventory domain models
from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Название")),
                ("slug", models.SlugField(blank=True, max_length=150, unique=True, verbose_name="Код")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="inventory.assetcategory",
                        verbose_name="Родительская категория",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="AssetTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=60, unique=True, verbose_name="Тег")),
                ("color", models.CharField(default="#0ea5e9", max_length=12, verbose_name="Цвет")),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Тег оборудования",
                "verbose_name_plural": "Теги оборудования",
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="Локация")),
                ("code", models.CharField(max_length=32, unique=True, verbose_name="Код")),
                ("address", models.CharField(blank=True, max_length=255, verbose_name="Адрес")),
                ("description", models.TextField(blank=True, verbose_name="Комментарий")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активна")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="managed_locations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Контакт",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Локация",
                "verbose_name_plural": "Локации",
            },
        ),
        migrations.CreateModel(
            name="Vendor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="Поставщик")),
                ("website", models.URLField(blank=True, verbose_name="Сайт")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("notes", models.TextField(blank=True, verbose_name="Заметки")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Поставщик",
                "verbose_name_plural": "Поставщики",
            },
        ),
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, verbose_name="Название")),
                ("inventory_code", models.CharField(max_length=64, unique=True, verbose_name="Инвентарный номер")),
                ("serial_number", models.CharField(blank=True, max_length=128, verbose_name="Серийный номер")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("available", "В наличии"),
                            ("in_use", "Выдано"),
                            ("reserved", "Зарезервировано"),
                            ("maintenance", "Обслуживание"),
                            ("lost", "Утеряно"),
                            ("retired", "Списано"),
                        ],
                        default="available",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "condition",
                    models.CharField(
                        choices=[
                            ("new", "Новый"),
                            ("good", "Отличное"),
                            ("normal", "Хорошее"),
                            ("needs_repair", "Требует ремонта"),
                            ("broken", "Неисправно"),
                        ],
                        default="new",
                        max_length=20,
                        verbose_name="Состояние",
                    ),
                ),
                ("purchase_date", models.DateField(blank=True, null=True, verbose_name="Дата закупки")),
                ("purchase_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="Стоимость")),
                ("warranty_expiration", models.DateField(blank=True, null=True, verbose_name="Гарантия до")),
                ("specs", models.JSONField(blank=True, default=dict, verbose_name="Характеристики")),
                ("notes", models.TextField(blank=True, verbose_name="Заметки")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_assets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Выдан пользователю",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="assets",
                        to="inventory.assetcategory",
                        verbose_name="Категория",
                    ),
                ),
                (
                    "custodian",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="custodian_assets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Ответственный",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assets",
                        to="inventory.location",
                        verbose_name="Локация",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(blank=True, related_name="assets", to="inventory.assettag", verbose_name="Теги"),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assets",
                        to="inventory.vendor",
                        verbose_name="Поставщик",
                    ),
                ),
            ],
            options={
                "ordering": ("name", "inventory_code"),
                "verbose_name": "Оборудование",
                "verbose_name_plural": "Оборудование",
            },
        ),
        migrations.CreateModel(
            name="MaintenanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160, verbose_name="Название")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("service", "Плановое обслуживание"),
                            ("repair", "Ремонт"),
                            ("update", "Обновление ПО"),
                            ("inspection", "Осмотр"),
                        ],
                        default="service",
                        max_length=20,
                        verbose_name="Тип",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "Запланировано"),
                            ("in_progress", "В процессе"),
                            ("done", "Завершено"),
                            ("canceled", "Отменено"),
                        ],
                        default="planned",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("scheduled_for", models.DateField(blank=True, null=True, verbose_name="Запланировано на")),
                ("completed_at", models.DateField(blank=True, null=True, verbose_name="Завершено")),
                ("description", models.TextField(blank=True, verbose_name="Описание работ")),
                ("cost", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name="Стоимость")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "asset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="maintenance", to="inventory.asset", verbose_name="Оборудование"),
                ),
                (
                    "contractor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="maintenance_records",
                        to="inventory.vendor",
                        verbose_name="Подрядчик",
                    ),
                ),
                (
                    "responsible",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="maintenance_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Ответственный",
                    ),
                ),
            ],
            options={
                "ordering": ("-scheduled_for", "-created_at"),
                "verbose_name": "Обслуживание",
                "verbose_name_plural": "Обслуживание",
            },
        ),
        migrations.CreateModel(
            name="AssetAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=160, verbose_name="Название")),
                ("file", models.FileField(blank=True, null=True, upload_to="assets/attachments/", verbose_name="Файл")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, verbose_name="Загружено")),
                (
                    "asset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="inventory.asset", verbose_name="Оборудование"),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="asset_attachments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Загрузил",
                    ),
                ),
            ],
            options={
                "verbose_name": "Файл оборудования",
                "verbose_name_plural": "Файлы оборудования",
            },
        ),
        migrations.CreateModel(
            name="AssetLogEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("created", "Создание"),
                            ("updated", "Изменение"),
                            ("status_change", "Смена статуса"),
                            ("assigned", "Выдача"),
                            ("returned", "Возврат"),
                            ("maintenance", "Обслуживание"),
                            ("note", "Комментарий"),
                        ],
                        max_length=32,
                        verbose_name="Действие",
                    ),
                ),
                ("from_status", models.CharField(blank=True, max_length=20, verbose_name="Статус до")),
                ("to_status", models.CharField(blank=True, max_length=20, verbose_name="Статус после")),
                ("notes", models.TextField(blank=True, verbose_name="Комментарий")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Время")),
                (
                    "asset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="log_entries", to="inventory.asset", verbose_name="Оборудование"),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="asset_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Ответственный",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Журнал операции",
                "verbose_name_plural": "Журнал операций",
            },
        ),
    ]
