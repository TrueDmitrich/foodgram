from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import empty

from api.serializers_fields_validators import (
    empty_list, unique_ingredients, unique_tags, Base64ImageField)
from recipes.constants import MIN_VALUE_TO_INGREDIENT_AMOUNT
from recipes.models import Tag, Ingredient, Recipe, IngredientsForRecipe


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Отображение пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar']

    def get_is_subscribed(self, profile_owner):
        if self.context['request'].user.is_authenticated:
            return profile_owner in self.context['request'].user.follows.all()
        return False

    def run_validation(self, data=empty):
        if self.context['request'].method == 'PUT':
            self.fields.fields['avatar'].required = True
        return super().run_validation(data)


class UserFollRecipeSerializer(UserSerializer):
    """Выдача списка подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'recipes',
            'recipes_count'
        ]

    def get_gs(self, user):
        return Recipe.objects.filter(author=user)

    def get_recipes(self, user):
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', 10**10))
        return SpecialRecipeSerializer(
            self.get_gs(user)[:recipes_limit], many=True).data

    def get_recipes_count(self, user):
        return self.get_gs(user).count()


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
    """Отображение ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def validate_amount(self, amount):
        if amount <= MIN_VALUE_TO_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше '
                f'либо равно {MIN_VALUE_TO_INGREDIENT_AMOUNT}.')
        return amount


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Общие настройки RecipeSerializers."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        ]


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
        qs = IngredientsForRecipe.objects.filter(
            recipe=recipe).select_related('ingredient')
        return IngredientForRecipeSerializer(qs, many=True).data

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, recipe):
        if not self.get_user().is_authenticated:
            return False
        favorite_recipes = self.get_user().favorite_recipes.all()
        if favorite_recipes:
            return (recipe.id in list(
                favorite_recipes.values_list('recipe_id'))[0])
        return False

    def get_is_in_shopping_cart(self, recipe):
        if not self.get_user().is_authenticated:
            return False
        shop_list_recipes = self.get_user().shop_list.all()
        if shop_list_recipes:
            return (recipe.id in list(
                shop_list_recipes.values_list('recipe_id'))[0])
        return False


class SpecialRecipeSerializer(BaseRecipeSerializer):
    """Вариант отображения для смежных задач."""

    class Meta(BaseRecipeSerializer.Meta):
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeCreateUpdateSerializer(BaseRecipeSerializer):
    """Создание рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientForRecipeSerializer(many=True)

    class Meta(BaseRecipeSerializer.Meta):
        pass

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context['request']}).data

    def validate_ingredients(self, ingredients):
        empty_list(ingredients)
        unique_ingredients(ingredients)
        return ingredients

    def validate_tags(self, tags):
        empty_list(tags)
        unique_tags(tags)
        return tags

    def get_user(self):
        return self.context['request'].user

    def tags_create(self, tags, recipe):
        tags_objects = [
            Recipe.tags.through(tag=tag, recipe=recipe) for tag in tags]
        Recipe.tags.through.objects.bulk_create(tags_objects)

    def ingredients_create(self, ingredients, recipe):
        ingredients_objects = [
            IngredientsForRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'])
            for ingredient in ingredients]
        IngredientsForRecipe.objects.bulk_create(ingredients_objects)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(
            **validated_data, author=self.get_user())
        self.tags_create(tags, recipe)
        self.ingredients_create(ingredients, recipe)
        recipe.refresh_from_db()
        return recipe

    def update(self, recipe, validated_data):
        tags = empty_list(validated_data.pop('tags', []))
        ingredients_list = empty_list(validated_data.pop('ingredients', []))
        tags_already_exist = [tag for tag in recipe.tags.all()]
        ingredients_already_exist = [ing for ing in recipe.ingredients.all()]
        ingredients = [ing['ingredient'] for ing in ingredients_list]
        if set(tags_already_exist) != set(tags):
            recipe.tags.through.objects.all().delete()
            self.tags_create(tags, recipe)
        if set(ingredients_already_exist) != set(ingredients):
            recipe.ingredients.through.objects.all().delete()
            self.ingredients_create(ingredients_list, recipe)
        return super().update(recipe, validated_data)
