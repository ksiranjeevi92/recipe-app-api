from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase


from rest_framework import status
from rest_framework.test import APIClient


from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')

def detial_url(tag_id):
    """Create and return tag detaisl id"""
    return reverse("recipe:tag-detail", args=[tag_id])

def create_user(email='test@gmail.com', password='password'):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagAPITest(TestCase):
    """Test Unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ProvateTagAPITest(TestCase):
    """Test Authenticated API Request"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by("-name")

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test"""
        user2 = create_user(email='email2@gmail.com')

        Tag.objects.create(user=user2, name='Fruity')

        tag = Tag.objects.create(user=self.user, name='Comfort')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], tag.name)

    def test_tag_update(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}

        url = detial_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()

        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name="BreakFast")

        url = detial_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)

        self.assertFalse(tags.exists())