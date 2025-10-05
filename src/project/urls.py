from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("accounts/", include(("src.apps.accounts.urls", "accounts"), namespace="accounts")),
    path("inventory/", include(("src.apps.inventory.urls", "inventory"), namespace="inventory")),
    path("tasks/", include(("src.apps.tasks.urls", "tasks"), namespace="tasks")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
