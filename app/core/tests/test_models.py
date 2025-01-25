from django.test import TestCase

from django.contrib.auth import get_user_model
from decimal import Decimal

from core import models


class ModelTests(TestCase):

    def test_create_user_with_eamil_succesful(self):
        email = 'test@gmail.com'
        password = 'testpassword'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_email_normalised(self):
        sample_emails = [
            ['test@GMAIL.com', 'test@gmail.com']
        ]

        for email , expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample1223')
            self.assertEqual(user.email, expected)


    def test_new_user_with_email_rises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample1243")
    
    def test_create_super_user_sucess(self):
        email ='test@gmail.com'
        password = 'sample'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test create recipe successfully"""
        user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title  = "Sample receipe title",
            time_minutes=5,
            price=Decimal('5.5'),
            description="Sample Receipe description"
        )

        self.assertEqual(str(recipe), recipe.title)


