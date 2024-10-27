from django.contrib.auth import get_user_model
from django.db.models import Value
from rest_framework import viewsets, permissions

from api.models import Tag, Ingredient, Recipe
from api.serializers import UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer

User = get_user_model()

#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     # permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

# Гига-костыль
    def get_queryset(self):
        user_favorite_recipes = self.request.user.favorite_recipes.all()
        user_shop_list = self.request.user.shop_list.all()
        queryset = Recipe.objects.all().select_related('ingredients', 'tags', 'author'
        ).annotate(is_favorited=Value(0), is_in_shopping_cart=Value(0))
        for recipe in queryset:
            if recipe in user_favorite_recipes:
                recipe.is_favorited = 1
            if recipe in user_shop_list:
                recipe.is_in_shopping_cart = 1
        return queryset