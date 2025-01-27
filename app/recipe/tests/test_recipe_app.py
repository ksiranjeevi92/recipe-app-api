from decimal import Decimal
import tempfile
import os
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

RECIPE_URL = reverse("recipe:recipe-list",)

def recipe_details_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


from core.models import (
    Recipe,
    Tag,
    Ingredient
    )

from recipe.serializers import (RecipeSerializer, RecipeDetailSerailizer)

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

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

    def test_create_recipe_with_new_tag(self):
        """Test Recipe with tag"""
        payload = {
            "title": "Thai Prawn curry",
            'time_minutes': 30,
            'price': Decimal('3.5'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exist = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()

            self.assertTrue(exist)

    def test_create_recipe_with_existing_tags(self):
        """Test Recipe with exisiting Tags"""
        tag_indian = Tag.objects.create(user=self.user,name='Indian')

        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('5.78'),
            'tags': [{'name': 'Indian'},{'name': 'Breakfast'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
                ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test Creating tag on update"""
        recipe = create_recipe(user=self.user )

        payload = {'tags': [{'name': "Lunch"}]}

        url = recipe_details_url(recipe_id=recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name="Lunch")

        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test Assign and Update tags"""
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")

        recipe = create_recipe(user=self.user)

        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

        payload = {'tags': [{'name': 'Lunch'}]}

        url = recipe_details_url(recipe_id=recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(tag_lunch, recipe.tags.all())

        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test Clearning a recipe tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')

        recipe = create_recipe(user=self.user)

        recipe.tags.add(tag)

        payload = {'tags': []}

        url = recipe_details_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 0)
    
    def test_create_recipe_with_new_ingredient(self):
        """Test"""

        payload = {
            'title': "Cauliflower",
            'time_minutes': 60,
            'price': Decimal('5.5'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'salt'}]

        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existign_ingredient(self):
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Lemon'
        )

        payload = {
            'title': 'Soup',
            'time_minutes': 5,
            'price': Decimal('2.55'),
            'ingredients': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)

        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()

            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test update"""                                               
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'Limes'}]}

        url = recipe_details_url(recipe_id=recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')

        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test updating a recipe to assign an ingredient."""
        # Create initial ingredient and recipe
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        # Create another ingredient to assign
        ingredient2 = Ingredient.objects.create(user=self.user, name='Chilli')

        # Payload to update recipe ingredients
        payload = {'ingredients': [{'name': 'Chilli'}]}
        url = recipe_details_url(recipe_id=recipe.id)

        # Send PATCH request to update recipe
        res = self.client.patch(url, payload)

        # Ensure the response status is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_clear_recipe_ingredient(self):
        """Test cleanig recipe"""
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")

        recipe = create_recipe(user=self.user)

        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}

        url = recipe_details_url(recipe_id=recipe.id)

        res= self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test Filtering Tag"""
        r1 = create_recipe(user=self.user, title='Currey')
        r2 = create_recipe(user=self.user, title="sweet")

        tag1 = Tag.objects.create(user=self.user,name="Vegan")
        tag2 = Tag.objects.create(user=self.user, name="Sweet")

        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and Chips')

        params = {'tags': f'{tag1.id}, {tag2.id}'}

        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)

        s2 = RecipeSerializer(r2)

        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        r1 = create_recipe(user=self.user, title='Rush Beans on Toast')
        r2 = create_recipe(user=self.user, title="Chicken")

        in1 = Ingredient.objects.create(user=self.user, name='Feta Cheese')
        in2 = Ingredient.objects.create(user=self.user, name='Chicken')

        r1.ingredients.add(in1)
        r2.ingredients.add(in2)

        r3 = create_recipe(user=self.user, title="Red")

        params = {'ingredients': f'{in1.id}, {in2.id}'}

        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)

        s2 = RecipeSerializer(r2)

        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)




class ImageUploadTest(TestCase):
    """Test ImageUpload api"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='image@gmail.com',
            password='image'
        )

        self.client.force_authenticate(self.user)

        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()
    
    def test_upload_image(self):
        """Test uploading"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}

            res = self.client.post(url, payload, format='multipart')

            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)



                                               

        

    