from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTestCases(TestCase):
    def setUp(self):
        email = 'jet@gmail.com'
        password = 'password'
        self.admin_user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.client = Client()

        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(email="sample@gmail.com", password=password)

    def test_user_list(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)
        
    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

