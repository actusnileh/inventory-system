from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Department, User


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="demo",
            email="demo@example.com",
            password="StrongPass!123",
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_success_redirects(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "demo", "password": "StrongPass!123"},
            follow=True,
        )
        self.assertRedirects(response, reverse("tasks:board"))
        self.assertIn("_auth_user_id", self.client.session)


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="HR", slug="hr")

    def test_registration_page_renders(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_registration_creates_user_with_user_role(self):
        payload = {
            "username": "newbie",
            "first_name": "New",
            "last_name": "User",
            "email": "newbie@example.com",
            "department": self.department.pk,
            "password1": "StrongPass!123",
            "password2": "StrongPass!123",
        }
        response = self.client.post(reverse("accounts:register"), payload)
        self.assertRedirects(response, reverse("tasks:board"))
        created = get_user_model().objects.get(username="newbie")
        self.assertEqual(created.role, User.Role.USER)
        self.assertIn("_auth_user_id", self.client.session)


class TeamDirectoryViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT", slug="it")
        self.admin = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass!123",
            department=self.department,
        )
        self.admin.promote_to_admin()
        self.regular = get_user_model().objects.create_user(
            username="employee",
            email="employee@example.com",
            password="StrongPass!123",
        )

    def test_requires_authentication(self):
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_denies_non_admin_user(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_view(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:team_directory"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/team_directory.html")
        self.assertGreaterEqual(response.context["total_users"], 2)

    def test_admin_can_open_user_form(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:team_create"))
        self.assertEqual(response.status_code, 200)
        payload = {
            "username": "invited",
            "password1": "StrongPass!123",
            "password2": "StrongPass!123",
            "role": User.Role.USER,
        }
        post = self.client.post(reverse("accounts:team_create"), payload)
        self.assertRedirects(post, reverse("accounts:team_directory"))
        created = User.objects.get(username="invited")
        self.assertEqual(created.role, User.Role.USER)
        self.assertFalse(created.is_staff)

    def test_profile_update(self):
        self.client.force_login(self.regular)
        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Emp",
                "last_name": "Loyee",
                "email": "employee@example.com",
                "department": "",
                "job_title": "Инженер",
                "phone": "12345",
                "timezone": "Europe/Moscow",
                "bio": "Test",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.regular.refresh_from_db()
        self.assertEqual(self.regular.job_title, "Инженер")

    def test_department_create(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("accounts:department_create"),
            {"name": "Support", "slug": "support", "description": "", "color": "#123456"},
        )
        self.assertRedirects(response, reverse("accounts:team_directory"))
        self.assertTrue(Department.objects.filter(slug="support").exists())

    def test_non_admin_cannot_access_team_create(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse("accounts:team_create"))
        self.assertEqual(response.status_code, 403)
