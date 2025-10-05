from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from .models import Asset, AssetCategory, MaintenanceRecord, Vendor


class AssetOverviewView(TemplateView):
    template_name = "inventory/asset_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = (
            Asset.objects.select_related("category", "location", "assigned_to", "custodian")
            .prefetch_related("tags")
            .order_by("name")
        )
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
            }
        )
        return context
