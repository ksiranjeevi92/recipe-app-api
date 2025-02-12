"""Test Ingredient API"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL=reverse('recipe:ingredient-list')

def detais_url(ingredeint_id):
    """create And return id"""
    return reverse("recipe:ingredient-detail", args=[ingredeint_id])


def create_user(email='user@example.com', password="test"):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientAPiTest(TestCase):
    """Test Unauthroized"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test"""
        res= self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientAPITest(TestCase):
    """Test Autherincated API"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def retrieve_ingredients(self):
        """Test Retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.object.crete(user=self.user, name="vanilla")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.object.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredeients_limited_to_user(self):
        user2 = create_user(email='user2@gmail.com')

        Ingredient.objects.create(user=user2, name="Salt")

        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
    
    def test_update_ingredient(self):
        """Test"""

        ingredient = Ingredient.objects.create(user=self.user, name="Cli")


        payload = {"name": "Coriander"}

        url = detais_url(ingredient.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting a Ingredienat"""

        ingredeint = Ingredient.objects.create(user=self.user, name="Lattue")

        url = detais_url(ingredeint.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredient = Ingredient.objects.filter(user=self.user)

        self.assertFalse(ingredient.exists())





