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
    UsersFavoriteRecipes, UsersShopRecipes, Follows)
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeWriteSerializer, SpecialRecipeSerializer,
    UserSerializer, UserImageSerializer,
    UserFollowsSerializer)


User = get_user_model()


def post_delete_check(request, manager, recipe):
    """Однотипные действия для shopping_cart, favorite."""

    if request.method == 'DELETE':
        get_object_or_404(
            manager, user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    _, created = manager.get_or_create(user=request.user, recipe=recipe)
    if not created:
        raise ValidationError('Рецепт уже добавлен!')
    return Response(
        data=SpecialRecipeSerializer(
            recipe, context={'request': request}).data,
        status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """API для продуктов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """API для рецептов."""

    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadOnly]

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
                         for r
                         in self.request.user.usersfavoriterecipess.all()]
                qs = qs.filter(pk__in=u_fav)
            if (
                'is_in_shopping_cart' in query) and (
                query['is_in_shopping_cart'] == '1'
            ):
                u_shop = [r.recipe.pk
                          for r in self.request.user.usersshoprecipess.all()]
                qs = qs.filter(pk__in=u_shop)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return Response({
            'short-link': request.build_absolute_uri(f'/s/{pk}')})

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, pk=None):
        recipes = [r.recipe for r in request.user.usersshoprecipess.all()]
        data = (IngredientsForRecipe.objects.filter(
            recipe__in=recipes).select_related('recipe', 'ingredient').values(
                'ingredient__name', 'amount', 'ingredient__measurement_unit'))
        shop_list = {}
        for values in data:
            ingredient, amount, m_u = values.values()
            if ingredient not in shop_list:
                shop_list[ingredient] = {
                    'amount': amount,
                    'measurement_unit': m_u,
                }
            else:
                shop_list[ingredient]['amount'] += amount
        content = 'Список покупок для рецептов: \n'
        for recipe in recipes:
            content += f' - {recipe.name}\n'
        content += '\nПродукты:\n'
        for name, ingredient in shop_list.items():
            content += (
                f' - {name} {ingredient["amount"]}'
                f' {ingredient["measurement_unit"]}\n')
        return FileResponse(content, 'rb')

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        return post_delete_check(
            request, UsersShopRecipes.objects, self.get_object())

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return post_delete_check(
            request, UsersFavoriteRecipes.objects, self.get_object())


class AuthViewSet(UserViewSet):
    """Дополненный viewset из Djoser."""

    serializer_class = UserSerializer
    permission_classes = (AuthorOrReadOnly,)

    @action(methods=['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserImageSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Очистка файлов с помощью django-cleanup
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user
        data = self.paginate_queryset(UserFollowsSerializer(
            User.objects.filter(pk__in=user.followers.all().select_related(
                'author').values('author')),
            context={'request': request}, many=True
        ).data)
        return self.get_paginated_response(data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        author = self.get_object()
        manager = Follows.objects
        if author == request.user:
            raise ValidationError('Нельзя подписаться или отписаться от себя!')
        if request.method == 'DELETE':
            get_object_or_404(
                Follows, user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, created = manager.get_or_create(user=request.user, author=author)
        if not created:
            raise ValidationError(f'Вы уже подписаны на {author}!')
        return Response(
            data=UserFollowsSerializer(
                self.get_object(), context={'request': request}).data,
            status=status.HTTP_201_CREATED)
