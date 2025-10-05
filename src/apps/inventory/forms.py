from django import forms
from django.contrib.auth import get_user_model

from .models import Asset, AssetCategory, Location, MaintenanceRecord, Vendor

User = get_user_model()


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = (
            "name",
            "category",
            "inventory_code",
            "serial_number",
            "status",
            "condition",
            "location",
            "custodian",
            "assigned_to",
            "tags",
            "vendor",
            "purchase_date",
            "purchase_price",
            "warranty_expiration",
            "specs",
            "notes",
        )
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "warranty_expiration": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "specs": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "purchase_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = AssetCategory.objects.order_by("name")
        self.fields["location"].queryset = Location.objects.order_by("name")
        self.fields["vendor"].queryset = Vendor.objects.order_by("name")
        self.fields["custodian"].queryset = User.objects.order_by("username")
        self.fields["assigned_to"].queryset = User.objects.order_by("username")
        for name, field in self.fields.items():
            if name in {"tags"}:
                field.widget.attrs.update({"class": "form-select", "multiple": "multiple"})
                continue
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            elif isinstance(field.widget, forms.Textarea):
                continue
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")
        self.fields["tags"].widget.attrs.setdefault("class", "form-select")


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ("name", "code", "address", "description", "contact", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = User.objects.order_by("username")
        for name, field in self.fields.items():
            if name == "is_active":
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            elif isinstance(field.widget, forms.Textarea):
                continue
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ("name", "website", "email", "phone", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                continue
            field.widget.attrs.setdefault("class", "form-control form-control-lg")


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ("name", "slug", "description", "parent")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = AssetCategory.objects.order_by("name")
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            elif isinstance(field.widget, forms.Textarea):
                continue
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = (
            "asset",
            "title",
            "kind",
            "status",
            "scheduled_for",
            "completed_at",
            "description",
            "cost",
            "responsible",
            "contractor",
        )
        widgets = {
            "scheduled_for": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "completed_at": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset"].queryset = Asset.objects.order_by("name")
        self.fields["responsible"].queryset = User.objects.order_by("username")
        self.fields["contractor"].queryset = Vendor.objects.order_by("name")
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            elif isinstance(field.widget, forms.Textarea):
                continue
            else:
                field.widget.attrs.setdefault("class", "form-control form-control-lg")
