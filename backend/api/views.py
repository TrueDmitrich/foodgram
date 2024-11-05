from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.filters import NameSearchFilter
from recipes.models import (
    Tag, Ingredient, Recipe, IngredientsForRecipe,
    UsersFavoriteRecipes, UsersShopRecipes, UsersFollows)
from api.permissions import RecipesPermission, UserPermission
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeCreateUpdateSerializer, SpecialRecipeSerializer,
    UserSerializer, UserImageSerializer,
    UserFollRecipeSerializer)


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
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)


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
                u_fav = [r.recipe.pk
                         for r in self.request.user.favorite_recipes.all()]
                qs = qs.filter(pk__in=u_fav)
            if (
                'is_in_shopping_cart' in query) and (
                query['is_in_shopping_cart'] == '1'
            ):
                u_shop = [r.recipe.pk
                          for r in self.request.user.shop_list.all()]
                qs = qs.filter(pk__in=u_shop)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        data = {
            'short-link': request.build_absolute_uri(
                f'/recipes/{self.get_object().id}')
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, pk=None):
        recipes = [r.recipe for r in request.user.shop_list.all()]
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
                f' {shop_list[key]["measurement_unit"]}\n')
        return FileResponse(content, 'rb')

    def post_delete_ckeck(self, request, db, recipe):
        """Однотипные действия для shopping_cart, favorite."""
        if request.method == 'POST':
            note, created = db.get_or_create(user=request.user, recipe=recipe)
            if not created:
                raise ValidationError('Рецепт уже добавлен!')
            return Response(
                data=SpecialRecipeSerializer(
                    self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                db.all(), user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.post_delete_ckeck(
            request, UsersShopRecipes.objects, self.get_object())

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return self.post_delete_ckeck(
            request, UsersFavoriteRecipes.objects, self.get_object())


class AuthViewSet(UserViewSet):
    """Дополненный viewset из Djoser."""

    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

    @action(methods=['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserImageSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user
        foll = [u.author for u in user.follows.all().select_related('author')]
        data = self.paginate_queryset(UserFollRecipeSerializer(
            foll, context={'request': request}, many=True
        ).data)
        return self.get_paginated_response(data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        author = self.get_object()
        db = UsersFollows.objects
        if author == request.user:
            raise ValidationError('Нельзя подписаться или отписаться от себя!')
        if request.method == 'POST':
            note, created = db.get_or_create(user=request.user, author=author)
            if not created:
                raise ValidationError(f'Вы уже подписаны на {author}!')
            return Response(
                data=UserFollRecipeSerializer(
                    self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                db.all(), user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
