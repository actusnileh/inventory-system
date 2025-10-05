from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView

from src.apps.accounts.mixins import AdminRequiredMixin

from .forms import (
    AssetCategoryForm,
    AssetForm,
    LocationForm,
    MaintenanceRecordForm,
    VendorForm,
)
from .models import Asset, AssetCategory, Location, MaintenanceRecord, Vendor


class AssetOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/asset_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = Asset.objects.select_related("category", "location", "assigned_to", "custodian").order_by("name")
        status_breakdown = assets.values("status").annotate(total=Count("id")).order_by("-total")
        category_breakdown = (
            AssetCategory.objects.annotate(asset_total=Count("assets")).order_by("-asset_total")
        )
        upcoming_maintenance = (
            MaintenanceRecord.objects.select_related("asset", "responsible")
            .filter(
                status__in=[MaintenanceRecord.Status.PLANNED, MaintenanceRecord.Status.IN_PROGRESS],
                scheduled_for__isnull=False,
            )
            .order_by("scheduled_for")[:6]
        )
        low_stock_assets = assets.filter(
            Q(status=Asset.Status.RESERVED) | Q(status=Asset.Status.MAINTENANCE)
        )[:6]

        context.update(
            {
                "assets": assets[:25],
                "asset_total": assets.count(),
                "status_breakdown": status_breakdown,
                "category_breakdown": category_breakdown,
                "vendor_count": Vendor.objects.count(),
                "upcoming_maintenance": upcoming_maintenance,
                "low_stock_assets": low_stock_assets,
                "current_date": timezone.now().date(),
                "can_manage": getattr(self.request.user, "is_admin_role", False),
            }
        )
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "inventory/asset_detail.html"
    context_object_name = "asset"
    queryset = Asset.objects.select_related(
        "category",
        "location",
        "vendor",
        "custodian",
        "assigned_to",
    )


class AssetCreateView(AdminRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "inventory/asset_form.html"
    success_url = reverse_lazy("inventory:asset_list")
    extra_context = {"asset": None}

    def form_valid(self, form):
        messages.success(self.request, "Оборудование добавлено")
        return super().form_valid(form)


class AssetUpdateView(AdminRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "inventory/asset_form.html"
    success_url = reverse_lazy("inventory:asset_list")
    context_object_name = "asset"

    def form_valid(self, form):
        messages.success(self.request, "Запись обновлена")
        return super().form_valid(form)


class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "inventory/location_form.html"
    success_url = reverse_lazy("inventory:asset_list")

    def form_valid(self, form):
        messages.success(self.request, "Локация создана")
        return super().form_valid(form)


class VendorCreateView(AdminRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = "inventory/vendor_form.html"
    success_url = reverse_lazy("inventory:asset_list")

    def form_valid(self, form):
        messages.success(self.request, "Поставщик добавлен")
        return super().form_valid(form)


class AssetCategoryCreateView(AdminRequiredMixin, CreateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:asset_list")

    def form_valid(self, form):
        messages.success(self.request, "Категория создана")
        return super().form_valid(form)


class MaintenanceCreateView(AdminRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = "inventory/maintenance_form.html"
    success_url = reverse_lazy("inventory:asset_list")

    def form_valid(self, form):
        messages.success(self.request, "Обслуживание запланировано")
        return super().form_valid(form)
