from django.urls import path

from .views import (
    AssetCategoryCreateView,
    AssetCreateView,
    AssetDetailView,
    AssetOverviewView,
    AssetUpdateView,
    LocationCreateView,
    MaintenanceCreateView,
    VendorCreateView,
)

app_name = "inventory"

urlpatterns = [
    path("", AssetOverviewView.as_view(), name="asset_list"),
    path("assets/add/", AssetCreateView.as_view(), name="asset_create"),
    path("assets/<int:pk>/", AssetDetailView.as_view(), name="asset_detail"),
    path("assets/<int:pk>/edit/", AssetUpdateView.as_view(), name="asset_update"),
    path("categories/add/", AssetCategoryCreateView.as_view(), name="category_create"),
    path("locations/add/", LocationCreateView.as_view(), name="location_create"),
    path("vendors/add/", VendorCreateView.as_view(), name="vendor_create"),
    path("maintenance/add/", MaintenanceCreateView.as_view(), name="maintenance_create"),
]
