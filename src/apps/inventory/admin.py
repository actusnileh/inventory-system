from __future__ import annotations

from django.contrib import admin
from django.db.models import Count

from .models import (
    Asset,
    AssetAttachment,
    AssetCategory,
    AssetLogEntry,
    AssetTag,
    Location,
    MaintenanceRecord,
    Vendor,
)


class AssetAttachmentInline(admin.TabularInline):
    model = AssetAttachment
    extra = 0
    fields = ("title", "file", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class AssetLogInline(admin.TabularInline):
    model = AssetLogEntry
    extra = 0
    fields = ("created_at", "action", "performed_by", "from_status", "to_status", "notes")
    readonly_fields = fields
    can_delete = False


class MaintenanceInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = (
        "title",
        "kind",
        "status",
        "scheduled_for",
        "completed_at",
        "responsible",
        "contractor",
    )
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "inventory_code",
        "name",
        "category",
        "status",
        "condition",
        "location",
        "assigned_to",
        "custodian",
        "purchase_date",
    )
    list_filter = (
        "status",
        "condition",
        "category",
        "location",
        "vendor",
        "tags",
    )
    search_fields = ("name", "inventory_code", "serial_number")
    autocomplete_fields = ("category", "location", "custodian", "assigned_to", "vendor", "tags")
    inlines = (AssetAttachmentInline, MaintenanceInline, AssetLogInline)
    readonly_fields = ("created_at", "updated_at")
    actions = ("mark_available", "mark_in_use", "mark_maintenance")
    list_select_related = ("category", "location", "assigned_to", "custodian")
    date_hierarchy = "purchase_date"

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "category",
                "inventory_code",
                "serial_number",
                "status",
                "condition",
                "tags",
            )
        }),
        ("Расположение", {
            "fields": (
                "location",
                "custodian",
                "assigned_to",
            )
        }),
        ("Закупка", {
            "fields": (
                "vendor",
                "purchase_date",
                "purchase_price",
                "warranty_expiration",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "specs",
                "notes",
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.action(description="Пометить как доступное")
    def mark_available(self, request, queryset):
        updated = queryset.update(status=Asset.Status.AVAILABLE)
        self.message_user(request, f"Статус обновлён для {updated} позиций")

    @admin.action(description="Пометить как выданное")
    def mark_in_use(self, request, queryset):
        updated = queryset.update(status=Asset.Status.IN_USE)
        self.message_user(request, f"Статус обновлён для {updated} позиций")

    @admin.action(description="Отправить на обслуживание")
    def mark_maintenance(self, request, queryset):
        updated = queryset.update(status=Asset.Status.MAINTENANCE)
        self.message_user(request, f"Статус обновлён для {updated} позиций")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_maintenance_count=Count("maintenance"))


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "contact", "is_active")
    search_fields = ("name", "code", "address")
    list_filter = ("is_active",)
    autocomplete_fields = ("contact",)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "website")
    search_fields = ("name", "email", "phone")


@admin.register(AssetTag)
class AssetTagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "asset",
        "kind",
        "status",
        "scheduled_for",
        "completed_at",
        "responsible",
    )
    list_filter = ("kind", "status", "scheduled_for")
    search_fields = ("title", "asset__name", "asset__inventory_code")
    autocomplete_fields = ("asset", "responsible", "contractor")
    readonly_fields = ("created_at", "updated_at", "is_overdue")


@admin.register(AssetLogEntry)
class AssetLogEntryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "asset", "action", "performed_by", "from_status", "to_status")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("asset__name", "asset__inventory_code", "notes")
    autocomplete_fields = ("asset", "performed_by")
    readonly_fields = ("created_at",)
