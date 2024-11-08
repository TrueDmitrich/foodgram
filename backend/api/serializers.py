from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as UserDjoserSerializer
from rest_framework import serializers

from api.serializers_fields_validators import (
    empty_list, Base64ImageField, validate_duplicates_in_list)
from recipes.constants import MIN_INGREDIENT_AMOUNT, MIN_RECIPE_COOK
from recipes.models import Tag, Ingredient, Recipe, IngredientsForRecipe


User = get_user_model()


class UserSerializer(UserDjoserSerializer):
    """Отображение пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False)

    class Meta(UserDjoserSerializer.Meta):
        fields = (*UserDjoserSerializer.Meta.fields, 'is_subscribed', 'avatar')

    def get_is_subscribed(self, profile_owner):
        return (self.context['request'].user.is_authenticated
                and profile_owner in self.context[
                    'request'].user.followers.all())


class UserFollowsSerializer(UserSerializer):
    """Пользователь с дополнительными полями рецептов."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        return SpecialRecipeSerializer(user.recipes.all()[:int(
            self.context['request'].query_params.get(
                'recipes_limit', 10**10))], many=True).data

    def get_recipes_count(self, user):
        return user.recipes.all().count()


class UserImageSerializer(serializers.ModelSerializer):
    """Для работы с avatar."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Отображение продуктов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class CommonRecipeSerializer(serializers.ModelSerializer):
    """Чистые поля Recipe."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class BaseRecipeSerializer(CommonRecipeSerializer):
    """Общие настройки RecipeSerializers."""

    image = Base64ImageField()

    class Meta(CommonRecipeSerializer.Meta):
        fields = (*CommonRecipeSerializer.Meta.fields,
                  'tags', 'ingredients')


class RecipeSerializer(BaseRecipeSerializer):
    """Отображение рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseRecipeSerializer.Meta):
        fields = (*BaseRecipeSerializer.Meta.fields,
                  'author', 'is_favorited', 'is_in_shopping_cart')

    def get_ingredients(self, recipe):
        return IngredientForRecipeSerializer(
            recipe.ingredientsforrecipe.all(), many=True).data

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, recipe):
        if not self.get_user().is_authenticated:
            return False
        favorite_recipes = self.get_user().usersfavoriterecipess.all()
        if favorite_recipes:
            return (recipe.id in list(
                favorite_recipes.values_list('recipe_id'))[0])
        return False

    def get_is_in_shopping_cart(self, recipe):
        if not self.get_user().is_authenticated:
            return False
        shop_list_recipes = self.get_user().usersshoprecipess.all()
        if shop_list_recipes:
            return (recipe.id in list(
                shop_list_recipes.values_list('recipe_id'))[0])
        return False


class SpecialRecipeSerializer(serializers.ModelSerializer):
    """Вариант отображения для смежных задач."""

    image = Base64ImageField()

    class Meta(BaseRecipeSerializer.Meta):
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeWriteSerializer(BaseRecipeSerializer):
    """Создание рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientForRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=MIN_RECIPE_COOK)

    class Meta(BaseRecipeSerializer.Meta):
        pass

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context=self.context).data

    def validate_ingredients(self, ingredients):
        empty_list(ingredients)
        validate_duplicates_in_list(
            [ing['ingredient'] for ing in ingredients], 'продукты')
        return ingredients

    def validate_tags(self, tags):
        empty_list(tags)
        validate_duplicates_in_list(tags, 'теги')
        return tags

    def get_user(self):
        return self.context['request'].user

    def ingredients_create(self, ingredients, recipe):
        IngredientsForRecipe.objects.bulk_create(
            IngredientsForRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
            for ingredient in ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        validated_data['author'] = self.get_user()
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.ingredients_create(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = empty_list(validated_data.pop('tags', []))
        ingredients_list = empty_list(validated_data.pop('ingredients', []))
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.ingredients_create(ingredients_list, recipe)

        return super().update(recipe, validated_data)
