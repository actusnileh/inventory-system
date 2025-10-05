from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    ProfileUpdateView,
    RegisterView,
    TeamDirectoryView,
    TeamMemberCreateView,
    TeamMemberUpdateView,
    DepartmentCreateView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("team/", TeamDirectoryView.as_view(), name="team_directory"),
    path("team/add/", TeamMemberCreateView.as_view(), name="team_create"),
    path("team/<int:pk>/edit/", TeamMemberUpdateView.as_view(), name="team_update"),
    path("team/departments/add/", DepartmentCreateView.as_view(), name="department_create"),
]
