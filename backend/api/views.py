from pprint import pprint

from django.contrib.auth import get_user_model
from django.db.models import Value
from rest_framework import viewsets, permissions, pagination, status
from rest_framework.response import Response

from api.models import Tag, Ingredient, Recipe
from api.permissions import IsUAu, RecipesPermission
from api.serializers import UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer, \
    IngredientForRecipeGetSerializer, RecipeCreateSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsUAu]

    def get_object(self):
        return super().get_object()

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """API для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """API для рецептов."""

    serializer_class = RecipeSerializer
    permission_classes = [RecipesPermission]
    pagination_class = pagination.PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_data = RecipeSerializer(recipe, context={'request': request})
        headers = self.get_success_headers(serializer_data.data)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_data = RecipeSerializer(recipe, context={'request': request})

        return Response(serializer_data.data)

    # def perform_create(self, serializer):
    #     serializer.save()


# Гига-костыль
# Мб проверку переделать для object_list
    def get_queryset(self):
        # user_favorite_recipes = self.request.user.favorite_recipes.all()
        # user_shop_list = self.request.user.shop_list.all()
        queryset = Recipe.objects.all().select_related('author')
        #
        # queryset = Recipe.objects.all().select_related('author'
        # ).annotate(is_favorited=Value(0), is_in_shopping_cart=Value(0))
        # # queryset = Recipe.objects.all().select_related('ingredients', 'tags', 'author'
        # # ).annotate(is_favorited=Value(0), is_in_shopping_cart=Value(0))
        # for recipe in queryset:
        #     if recipe in user_favorite_recipes:
        #         recipe.is_favorited = 1
        #     if recipe in user_shop_list:
        #         recipe.is_in_shopping_cart = 1
        # pprint(queryset.values_list())
        return queryset