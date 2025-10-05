from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("accounts:login")
    raise_exception = True

    def test_func(self) -> bool:  # pragma: no cover - simple boolean check
        return bool(self.request.user.is_authenticated and getattr(self.request.user, "is_admin_role", False))


__all__ = ["AdminRequiredMixin"]
