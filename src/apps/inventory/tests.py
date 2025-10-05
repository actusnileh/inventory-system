from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Asset, AssetCategory, Location, MaintenanceRecord, Vendor


class AssetOverviewViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.manager = user_model.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="inventory-pass",
        )
        self.category = AssetCategory.objects.create(name="Ноутбуки", slug="laptops")
        self.location = Location.objects.create(name="Склад", code="WH-01")
        self.vendor = Vendor.objects.create(name="TechVendor")
        self.asset = Asset.objects.create(
            name="MacBook Pro",
            category=self.category,
            inventory_code="INV-001",
            status=Asset.Status.IN_USE,
            condition=Asset.Condition.GOOD,
            location=self.location,
            custodian=self.manager,
            assigned_to=self.manager,
        )
        MaintenanceRecord.objects.create(
            asset=self.asset,
            title="Плановый сервис",
            scheduled_for=timezone.now().date(),
            responsible=self.manager,
        )
        self.admin = user_model.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="inventory-pass",
        )
        self.admin.promote_to_admin()

    def test_asset_overview_page_success(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("inventory:asset_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory/asset_overview.html")

    def test_context_contains_assets(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("inventory:asset_list"))
        assets = response.context["assets"]
        self.assertIn(self.asset, list(assets))
        self.assertGreaterEqual(response.context["asset_total"], 1)

    def test_status_breakdown_has_entries(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("inventory:asset_list"))
        breakdown = list(response.context["status_breakdown"])
        self.assertTrue(any(item["status"] == Asset.Status.IN_USE for item in breakdown))

    def test_create_requires_admin(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("inventory:asset_create"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_create(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventory:asset_create"))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_accessible(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("inventory:asset_detail", args=[self.asset.pk]))
        self.assertEqual(response.status_code, 200)
