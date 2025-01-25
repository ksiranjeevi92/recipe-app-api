from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

RECIPE_URL = reverse("recipe:recipe-list")

def recipe_details_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


from core.models import Recipe

from recipe.serializers import (RecipeSerializer, RecipeDetailSerailizer)

def create_recipe(user, **params):
    defaults = {
        'title': 'Sample Title',
        'time_minutes': 5,
        'description': 'Sample Description',
        'price': Decimal('5.5'),
        'link': 'http://exmple.com/recipe.pdf'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user,**defaults)

    return recipe

class PublicRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access the recipe API"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limit_user(self):
        other_user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='testpassword'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        res = self.client.get(recipe_details_url(recipe.id))

        serializer = RecipeDetailSerailizer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(
            res.status_code, status.HTTP_201_CREATED
        )


        

    