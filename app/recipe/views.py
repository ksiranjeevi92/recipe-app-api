

from rest_framework import (viewsets,mixins, )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import (Recipe, Tag, Ingredient)
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

class BaseRecipeAttrViewSet(
                            mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """Filter queryset ti authetincated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
    
class TagViewSet(
    BaseRecipeAttrViewSet
    ):
    """Manage tag in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
   

    
    
class IngredientViewSet(BaseRecipeAttrViewSet):
    
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    

    
 
