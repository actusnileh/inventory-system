from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from src.apps.inventory.models import Asset, MaintenanceRecord
from src.apps.tasks.models import Project, Task


def index(request):
    context = {
        "homepage": {
            "task_count": Task.objects.filter(is_archived=False).count(),
            "project_total": Project.objects.filter(is_active=True).count(),
            "asset_count": Asset.objects.count(),
            "maintenance_planned": MaintenanceRecord.objects.filter(
                status=MaintenanceRecord.Status.PLANNED
            ).count(),
            "next_maintenance": MaintenanceRecord.objects.filter(
                status=MaintenanceRecord.Status.PLANNED,
                scheduled_for__isnull=False,
            ).order_by("scheduled_for").values_list("scheduled_for", flat=True).first(),
        }
    }
    return render(request, "index.html", context)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("accounts/", include(("src.apps.accounts.urls", "accounts"), namespace="accounts")),
    path("inventory/", include(("src.apps.inventory.urls", "inventory"), namespace="inventory")),
    path("tasks/", include(("src.apps.tasks.urls", "tasks"), namespace="tasks")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
