from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from src.apps.accounts.models import Department
from src.apps.inventory.models import Asset, AssetCategory, Location, MaintenanceRecord, Vendor
from src.apps.tasks.models import Project, Task, TaskActivity, TaskComment


class Command(BaseCommand):
    help = "Populate the database with demo data for quick UI checks"

    def handle(self, *args, **options):
        with transaction.atomic():
            self._build_departments()
            users = self._build_users()
            assets = self._build_inventory(users)
            self._build_tasks(users, assets)
        self.stdout.write(self.style.SUCCESS("Demo data ready."))

    def _build_departments(self) -> None:
        departments = (
            ("ИТ", "Информационные технологии", "#1f3a8a"),
            ("Логистика", "Склад и доставка", "#0f766e"),
            ("HR", "Подбор и адаптация", "#a855f7"),
        )
        for name, description, color in departments:
            Department.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description, "color": color},
            )

    def _build_users(self) -> dict[str, object]:
        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username="demo_admin",
            defaults={
                "email": "demo.admin@example.com",
                "first_name": "Admin",
                "last_name": "Demo",
                "department": Department.objects.filter(name="ИТ").first(),
            },
        )
        if created:
            admin.set_password("Admin123!")
        admin.promote_to_admin()
        admin.save()

        manager, created = User.objects.get_or_create(
            username="demo_user",
            defaults={
                "email": "demo.user@example.com",
                "first_name": "Иван",
                "last_name": "Петров",
                "department": Department.objects.filter(name="Логистика").first(),
                "job_title": "Координатор склада",
            },
        )
        if created:
            manager.set_password("User123!")
            manager.save()

        analyst, created = User.objects.get_or_create(
            username="demo_analyst",
            defaults={
                "email": "analyst@example.com",
                "first_name": "Мария",
                "last_name": "Сидорова",
                "department": Department.objects.filter(name="HR").first(),
                "job_title": "HR-аналитик",
            },
        )
        if created:
            analyst.set_password("User123!")
            analyst.save()

        return {"admin": admin, "user": manager, "analyst": analyst}

    def _build_inventory(self, users: dict[str, object]) -> list[Asset]:
        laptop_category, _ = AssetCategory.objects.get_or_create(name="Ноутбуки", defaults={"slug": "laptops"})
        tools_category, _ = AssetCategory.objects.get_or_create(name="Оборудование", defaults={"slug": "tools"})

        hq, _ = Location.objects.get_or_create(
            code="HQ",
            defaults={"name": "Главный офис", "address": "Москва, Пресненская наб. 10", "contact": users["analyst"]},
        )
        warehouse, _ = Location.objects.get_or_create(
            code="WH-1",
            defaults={"name": "Склад №1", "address": "Москва, ул. Производственная 3", "contact": users["user"]},
        )

        vendor, _ = Vendor.objects.get_or_create(name="TechVendor", defaults={"email": "sales@techvendor.io"})

        asset_1, _ = Asset.objects.get_or_create(
            inventory_code="NB-001",
            defaults={
                "name": "MacBook Pro 14",
                "category": laptop_category,
                "status": Asset.Status.IN_USE,
                "condition": Asset.Condition.GOOD,
                "custodian": users["analyst"],
                "assigned_to": users["analyst"],
                "location": hq,
                "vendor": vendor,
                "purchase_date": date.today() - timedelta(days=200),
                "purchase_price": 220000,
            },
        )

        asset_2, _ = Asset.objects.get_or_create(
            inventory_code="EQ-010",
            defaults={
                "name": "Сканер штрихкодов",
                "category": tools_category,
                "status": Asset.Status.AVAILABLE,
                "condition": Asset.Condition.NORMAL,
                "location": warehouse,
                "vendor": vendor,
                "purchase_date": date.today() - timedelta(days=90),
                "purchase_price": 18000,
            },
        )

        MaintenanceRecord.objects.get_or_create(
            asset=asset_1,
            title="Чистка и проверка",
            defaults={
                "kind": MaintenanceRecord.Kind.INSPECTION,
                "status": MaintenanceRecord.Status.PLANNED,
                "scheduled_for": date.today() + timedelta(days=10),
                "responsible": users["admin"],
                "description": "Плановый осмотр техники.",
            },
        )

        return [asset_1, asset_2]

    def _build_tasks(self, users: dict[str, object], assets: list[Asset]) -> None:
        project, _ = Project.objects.get_or_create(
            code="onboarding",
            defaults={
                "name": "Онбординг сотрудников",
                "description": "Процесс адаптации новых сотрудников",
                "owner": users["admin"],
                "start_date": date.today() - timedelta(days=7),
            },
        )
        project.members.add(users["admin"], users["user"], users["analyst"])

        task_1, _ = Task.objects.get_or_create(
            project=project,
            title="Выдать ноутбуки",
            defaults={
                "description": "Подготовить и выдать ноутбуки новичкам",
                "status": Task.Status.IN_PROGRESS,
                "priority": Task.Priority.HIGH,
                "created_by": users["admin"],
                "assignee": users["user"],
                "start_date": date.today() - timedelta(days=2),
                "due_date": date.today() + timedelta(days=1),
            },
        )
        task_1.assets.set(assets[:1])
        task_1.watchers.add(users["analyst"])

        task_2, _ = Task.objects.get_or_create(
            project=project,
            title="Настроить учет оборудования",
            defaults={
                "description": "Проверить наличие и актуализировать данные в системе",
                "status": Task.Status.TODO,
                "priority": Task.Priority.NORMAL,
                "created_by": users["admin"],
                "assignee": users["analyst"],
                "start_date": date.today(),
                "due_date": date.today() + timedelta(days=5),
            },
        )
        task_2.assets.set(assets)
        task_2.watchers.add(users["user"])

        TaskComment.objects.get_or_create(
            task=task_1,
            author=users["admin"],
            message="Не забудьте проверить зарядные устройства.",
        )

        TaskComment.objects.get_or_create(
            task=task_2,
            author=users["user"],
            message="Данные со склада загружу до конца дня.",
        )

        TaskActivity.objects.get_or_create(
            task=task_1,
            action=TaskActivity.Action.STATUS,
            author=users["admin"],
            defaults={"payload": {"status": Task.Status.IN_PROGRESS}},
        )
