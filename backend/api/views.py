from pprint import pprint

from Tools.scripts.make_ctype import method
# from django.contrib.admin import action
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Value
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, pagination, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from urllib3 import request

from api.models import Tag, Ingredient, Recipe, IngredientsForRecipe
from api.permissions import IsUAu, RecipesPermission
from api.serializers import UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer, \
    IngredientForRecipeGetSerializer, RecipeCreateSerializer, RecipeShoplistFavoriteSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

    # def get_object(self):
    #     return super().get_object()

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """API для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """API для рецептов."""

    serializer_class = RecipeSerializer
    permission_classes = [RecipesPermission]
    # pagination_class = pagination.PageNumberPagination
    # filter_backends = (SearchFilter,)

    def get_queryset(self):
        qs = Recipe.objects.all().select_related('author').prefetch_related('tags')
        query = self.request.query_params
        if 'author' in query:
            qs = qs.filter(author__id=query['author'])
        if 'tags' in query:
            notes = Recipe.tags.through.objects.select_related('tag')
            tags = query.getlist('tags')
            passed_recipe_id = set([note.recipe_id for note in notes.filter(tag__name__in=tags)])
            qs = qs.filter(pk__in=passed_recipe_id)

            # passed_recipe_id = set()
            # loop = 0
            # for tag in tags:
            #     loop_res = [note.recipe_id for note in notes.filter(tag__name=tag)]
            #     if loop == 0:
            #         passed_recipe_id = set(loop_res)
            #     else:
            #         passed_recipe_id.intersection_update(set(loop_res))
            #     loop += 1

            # qs = qs.filter(pk__in=passed_recipe_id)
        if self.request.user.is_authenticated:
            if ('is_favorited' in query) and query['is_favorited'] == '1':
                u_fav = [r.id for r in self.request.user.favorite_recipes.all()]
                qs = qs.filter(pk__in=u_fav)
            if ('is_in_shopping_cart' in query) and query['is_in_shopping_cart'] == '1':
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



# # Гига-костыль
# # Мб проверку переделать для object_list
#     def get_queryset(self):
#         # user_favorite_recipes = self.request.user.favorite_recipes.all()
#         # user_shop_list = self.request.user.shop_list.all()
#         queryset = Recipe.objects.all().select_related('author')
#         #
#         # queryset = Recipe.objects.all().select_related('author'
#         # ).annotate(is_favorited=Value(0), is_in_shopping_cart=Value(0))
#         # # queryset = Recipe.objects.all().select_related('ingredients', 'tags', 'author'
#         # # ).annotate(is_favorited=Value(0), is_in_shopping_cart=Value(0))
#         # for recipe in queryset:
#         #     if recipe in user_favorite_recipes:
#         #         recipe.is_favorited = 1
#         #     if recipe in user_shop_list:
#         #         recipe.is_in_shopping_cart = 1
#         # pprint(queryset.values_list())
#         return queryset

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        if not pk:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {
            'short-link':request.build_absolute_uri().replace('get-link/', '')
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, pk=None):
        recipes = request.user.shop_list.all()
        ingredients = IngredientsForRecipe.objects.filter(recipe__in=recipes).select_related('ingredient')
        shop_list = {}
        for ing in ingredients:
            if ing.ingredient.name not in shop_list:
                shop_list[ing.ingredient.name] = {
                    # 'name': ing.ingredient.name,
                    'amount': ing.amount,
                    'measurement_unit': ing.ingredient.measurement_unit,
                }
            else:
                shop_list[ing.ingredient.name]['amount'] += ing.amount
        content = ''
        for key in shop_list.keys():
            content += f'{key} {shop_list[key]["amount"]} {shop_list[key]["measurement_unit"]}\n'
        with open('shop_list.txt', 'w', encoding='utf-8') as file_txt:
            file_txt.write(content)

        return FileResponse('shop_list.txt', 'rb')

# Допилить разрешения
    # Добавть проверку авторизации
# Объединить в одну функцию
    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):

        obj = self.get_object()
        DB = request.user.shop_list.through.objects

        if request.method == 'POST':
            if (DB.filter(user=request.user, recipe_id=obj.id,).exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            DB.create(
                user_id=request.user.id,
                recipe_id=obj.id,
            )
            return Response(
                # data=RecipeShoplistSerializer(self.get_object()).data,
                data=RecipeShoplistFavoriteSerializer(self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not (DB.filter(user=request.user, recipe_id=obj.id,).exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            DB.filter(
                user_id=request.user.id,
                recipe_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        obj = self.get_object()
        DB = request.user.favorite_recipes.through.objects
        if request.method == 'POST':
            if (DB.filter(user=request.user, recipe_id=obj.id).exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            DB.create(
                user_id=request.user.id,
                recipe_id=obj.id,
            )
            return Response(
                data=RecipeShoplistFavoriteSerializer(self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not (DB.filter(user=request.user, recipe_id=obj.id).exists()
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            DB.filter(
                user_id=request.user.id,
                recipe_id=obj.id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # http: // localhost / api / recipes / {id} / shopping_cart /
