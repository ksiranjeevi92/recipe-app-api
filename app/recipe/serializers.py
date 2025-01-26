from rest_framework import serializers
from core.models import (Recipe,Tag)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        ready_only_fields = ['id']

class RecipeDetailSerailizer(RecipeSerializer):
    """Serializer for recipe details vierw"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

