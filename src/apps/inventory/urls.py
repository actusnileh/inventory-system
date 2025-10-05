from django.urls import path

from .views import AssetOverviewView

app_name = "inventory"

urlpatterns = [
    path("", AssetOverviewView.as_view(), name="asset_list"),
]
