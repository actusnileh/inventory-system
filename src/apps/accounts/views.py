from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import (
    LoginForm,
    DepartmentForm,
    ProfileForm,
    RegistrationForm,
    TeamMemberCreateForm,
    TeamMemberUpdateForm,
)
from .mixins import AdminRequiredMixin
from .models import Department, User


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("tasks:board")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: LoginForm) -> HttpResponse:
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, "Рады видеть вас снова!")
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("tasks:board")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        user: User = form.save()
        raw_password = form.cleaned_data.get("password1")
        authenticated: AbstractBaseUser | None = authenticate(
            self.request, username=user.username, password=raw_password
        )
        if authenticated is not None:
            login(self.request, authenticated)
        messages.success(self.request, "Аккаунт создан. Добро пожаловать!")
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context


class LogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy("accounts:login")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)
        messages.info(request, "Вы вышли из аккаунта.")
        return redirect("index")


class TeamDirectoryView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/team_directory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        departments = (
            Department.objects.prefetch_related("users")
            .annotate(user_count=Count("users"))
            .order_by("name")
        )
        users = User.objects.select_related("department").order_by("username")
        context.update(
            {
                "departments": departments,
                "recent_users": users.order_by("-date_joined")[:8],
                "total_users": users.count(),
                "active_users": users.filter(is_active=True).count(),
                "role_distribution": (
                    users.values("role").annotate(total=Count("id")).order_by("-total")
                ),
            }
        )
        return context


class TeamMemberCreateView(AdminRequiredMixin, FormView):
    template_name = "accounts/team_member_form.html"
    form_class = TeamMemberCreateForm
    success_url = reverse_lazy("accounts:team_directory")
    extra_context = {"member": None}

    def form_valid(self, form: TeamMemberCreateForm) -> HttpResponse:
        user = form.save()
        messages.success(self.request, f"Пользователь {user.get_display_name()} добавлен")
        return super().form_valid(form)


class TeamMemberUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "accounts/team_member_form.html"
    form_class = TeamMemberUpdateForm
    model = User
    context_object_name = "member"
    success_url = reverse_lazy("accounts:team_directory")

    def form_valid(self, form: TeamMemberUpdateForm) -> HttpResponse:
        messages.success(self.request, "Данные пользователя обновлены")
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form: ProfileForm) -> HttpResponse:
        messages.success(self.request, "Профиль обновлён")
        return super().form_valid(form)


class DepartmentCreateView(AdminRequiredMixin, FormView):
    template_name = "accounts/department_form.html"
    form_class = DepartmentForm
    success_url = reverse_lazy("accounts:team_directory")

    def form_valid(self, form: DepartmentForm) -> HttpResponse:
        department = form.save()
        messages.success(self.request, f"Отдел {department.name} создан")
        return super().form_valid(form)


__all__ = [
    "LoginView",
    "RegisterView",
    "LogoutView",
    "TeamDirectoryView",
    "TeamMemberCreateView",
    "TeamMemberUpdateView",
    "ProfileUpdateView",
    "DepartmentCreateView",
]
