from django.contrib.auth import get_user_model
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.models import Tag, Ingredient, Recipe, IngredientsForRecipe
from api.permissions import RecipesPermission
from api.serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeCreateSerializer, RecipeShoplistFavoriteSerializer)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """API для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    """API для рецептов."""

    serializer_class = RecipeSerializer
    permission_classes = [RecipesPermission]

    def get_queryset(self):
        qs = Recipe.objects.all().select_related(
            'author').prefetch_related('tags')
        query = self.request.query_params
        if 'author' in query:
            qs = qs.filter(author__id=query['author'])
        if 'tags' in query:
            notes = Recipe.tags.through.objects.select_related('tag')
            tags = query.getlist('tags')
            passed_recipe_id = set([note.recipe_id for note in notes.filter(
                tag__name__in=tags)])
            qs = qs.filter(pk__in=passed_recipe_id)
        if self.request.user.is_authenticated:
            if ('is_favorited' in query) and query['is_favorited'] == '1':
                u_fav = [r.id
                         for r in self.request.user.favorite_recipes.all()]
                qs = qs.filter(pk__in=u_fav)
            if (
                'is_in_shopping_cart' in query) and (
                query['is_in_shopping_cart'] == '1'
            ):
                u_shop = [r.id for r in self.request.user.shop_list.all()]
                qs = qs.filter(pk__in=u_shop)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_data = RecipeSerializer(
            recipe, context={'request': request})
        headers = self.get_success_headers(serializer_data.data)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_data = RecipeSerializer(
            recipe, context={'request': request})
        return Response(serializer_data.data)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        if not pk:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {
            'short-link': request.build_absolute_uri().replace('get-link/', '')
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, pk=None):
        recipes = request.user.shop_list.all()
        ingredients = IngredientsForRecipe.objects.filter(
            recipe__in=recipes).select_related('ingredient')
        shop_list = {}
        for ing in ingredients:
            if ing.ingredient.name not in shop_list:
                shop_list[ing.ingredient.name] = {
                    'amount': ing.amount,
                    'measurement_unit': ing.ingredient.measurement_unit,
                }
            else:
                shop_list[ing.ingredient.name]['amount'] += ing.amount
        content = ''
        for key in shop_list.keys():
            content += (
                f'{key} {shop_list[key]["amount"]}'
                + f'{shop_list[key]["measurement_unit"]}\n')
        return FileResponse(content)

    def post_delete_ckeck(self, request, db, obj):
        """Однотипные действия для shopping_cart, favorite."""
        if request.method == 'POST':
            if (
                db.filter(user=request.user, recipe_id=obj.id,).exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            db.create(
                user_id=request.user.id,
                recipe_id=obj.id,
            )
            return Response(
                data=RecipeShoplistFavoriteSerializer(
                    self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            note = db.filter(user=request.user, recipe_id=obj.id)
            if not note.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        obj = self.get_object()
        db = request.user.shop_list.through.objects
        return self.post_delete_ckeck(request, db, obj)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        obj = self.get_object()
        db = request.user.favorite_recipes.through.objects
        return self.post_delete_ckeck(request, db, obj)
