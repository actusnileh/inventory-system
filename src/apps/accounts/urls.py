from django.urls import path
from django.contrib.auth import views as auth_views

from .views import TeamDirectoryView, RegisterView
from .forms import StyledAuthenticationForm

app_name = "accounts"

urlpatterns = [
    path("team/", TeamDirectoryView.as_view(), name="team_directory"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html", form_class=StyledAuthenticationForm),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="index"),
        name="logout",
    ),
]
