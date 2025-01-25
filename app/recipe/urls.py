from django.urls import (path, include)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()

router.register('recipe', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('recipe', include(router.get_urls()))
]