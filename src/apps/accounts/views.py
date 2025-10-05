from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .models import Department, User
from .forms import RegistrationForm


class TeamDirectoryView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/team_directory.html"
    login_url = reverse_lazy("accounts:login")

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


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:team_directory")

    def form_valid(self, form):
        user = form.save()
        backend = settings.AUTHENTICATION_BACKENDS[0]
        login(self.request, user, backend=backend)
        return super().form_valid(form)
