from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Department


class TeamDirectoryViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT", slug="it")
        self.user = get_user_model().objects.create_user(
            username="jdoe",
            email="jdoe@example.com",
            password="strong-pass",
            department=self.department,
            role="manager",
            job_title="Project Manager",
        )

    def test_team_directory_requires_auth(self):
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_team_directory_returns_success_for_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/team_directory.html")

    def test_context_contains_expected_statistics(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.context["total_users"], 1)
        self.assertEqual(response.context["active_users"], 1)
        self.assertIn(self.department, list(response.context["departments"]))

    def test_role_distribution_present(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:team_directory"))
        distribution = list(response.context["role_distribution"])
        self.assertTrue(any(item["role"] == "manager" for item in distribution))


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="HR", slug="hr")

    def test_registration_page_renders(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_registration_creates_user_and_logs_in(self):
        data = {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "department": self.department.pk,
            "password1": "StrongPass!123",
            "password2": "StrongPass!123",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertRedirects(response, reverse("accounts:team_directory"))
        user_model = get_user_model()
        self.assertTrue(user_model.objects.filter(username="newuser").exists())
        # Пользователь должен быть авторизован после регистрации
        self.assertIn("_auth_user_id", self.client.session)
