from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import path


def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
