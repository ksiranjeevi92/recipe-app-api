

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe
# Create your views here.

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeDetailSerailizer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return Serializer class for request"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class
    
    def perform_create(self,serializer):
        return serializer.save(user=self.request.user)
