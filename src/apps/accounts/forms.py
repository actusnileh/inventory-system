from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Department, User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=150, required=False)
    last_name = forms.CharField(label="Фамилия", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=False)
    department = forms.ModelChoiceField(
        label="Отдел",
        queryset=Department.objects.all(),
        required=False,
        empty_label="Не выбран",
    )
    job_title = forms.CharField(label="Должность", max_length=120, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "department",
            "job_title",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.order_by("name")
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing_classes + " form-control form-control-lg").strip()

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.department = self.cleaned_data.get("department")
        user.job_title = self.cleaned_data.get("job_title", "")
        user.role = User.Role.USER
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control form-control-lg").strip()


class TeamMemberCreateForm(UserCreationForm):
    department = forms.ModelChoiceField(
        label="Отдел",
        queryset=Department.objects.order_by("name"),
        required=False,
        empty_label="Не выбран",
    )
    role = forms.ChoiceField(label="Роль", choices=User.Role.choices)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
            "job_title",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control form-control-lg").strip()

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get("role", User.Role.USER)
        user.department = self.cleaned_data.get("department")
        user.job_title = self.cleaned_data.get("job_title", "")
        if user.role == User.Role.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        if commit:
            user.save()
        return user


class TeamMemberUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
            "job_title",
            "phone",
            "timezone",
            "is_active",
        )
        widgets = {
            field: forms.TextInput(attrs={"class": "form-control form-control-lg"})
            for field in ["first_name", "last_name", "email", "job_title", "phone"]
        }
        widgets.update(
            {
                "role": forms.Select(attrs={"class": "form-select form-select-lg"}),
                "department": forms.Select(attrs={"class": "form-select form-select-lg"}),
                "timezone": forms.TextInput(attrs={"class": "form-control form-control-lg"}),
                "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            }
        )

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        if user.role == User.Role.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.order_by("name")
        for name, field in self.fields.items():
            if name == "is_active":
                field.widget.attrs.setdefault("class", "form-check-input")
                continue
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select form-select-lg")
            else:
                css = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (css + " form-control form-control-lg").strip()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
            "department",
            "job_title",
            "phone",
            "timezone",
            "bio",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.order_by("name")
        self.fields["department"].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                continue
            css = "form-select form-select-lg" if isinstance(field.widget, forms.Select) else "form-control form-control-lg"
            field.widget.attrs["class"] = css


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "slug", "description", "color")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-lg"}),
            "slug": forms.TextInput(attrs={"class": "form-control form-control-lg"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
