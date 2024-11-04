from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers_fields_validators import (
    ImageBase64Field, empty_list, unique_ingredients, unique_tags)
from api.models import Tag, Ingredient, Recipe, IngredientsForRecipe
from users.serializers import UserSerializer


User = get_user_model()


class GetUser:
    """Пользователь из request."""

    def get_user(self):
        return self.context['request'].user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Ингредиенты для создания рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'amount',
        )


class IngredientForRecipeGetSerializer(serializers.ModelSerializer):
    """Отображение ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Общие настройки RecipeSerializers."""

    image = ImageBase64Field()

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


class RecipeSerializer(BaseRecipeSerializer, GetUser):
    """Отображение рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseRecipeSerializer.Meta):
        fields = (BaseRecipeSerializer.Meta.fields
                  + ['author', 'is_favorited', 'is_in_shopping_cart'])

    def get_ingredients(self, obj):
        qs = IngredientsForRecipe.objects.filter(
            recipe=obj).select_related('ingredient')
        return IngredientForRecipeGetSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        return (self.get_user().is_authenticated) and (
            obj in self.get_user().favorite_recipes.all())

    def get_is_in_shopping_cart(self, obj):
        return (self.get_user().is_authenticated) and (
            obj in self.get_user().shop_list.all())


class RecipeShoplistFavoriteSerializer(BaseRecipeSerializer):
    """Вариант отображения для смежных задач."""

    class Meta(BaseRecipeSerializer.Meta):
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeCreateSerializer(BaseRecipeSerializer, GetUser):
    """Создание рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientForRecipeCreateSerializer(many=True)

    class Meta(BaseRecipeSerializer.Meta):
        pass

    # на validators в поле не реагирует
    def validate_ingredients(self, value):
        empty_list(value)
        unique_ingredients(value)
        return value

    def validate_tags(self, value):
        empty_list(value)
        unique_tags(value)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(
            **validated_data, author=self.get_user())
        for tag in tags:
            Recipe.tags.through.objects.create(
                recipe_id=recipe.id, tag_id=tag.id)
        for ingredient in ingredients:
            Recipe.ingredients.through.objects.create(
                recipe_id=recipe.id,
                ingredient_id=ingredient['ingredient'].id,
                amount=ingredient['amount'],
            )
        recipe.refresh_from_db()
        return recipe

    def update(self, instance, validated_data):
        tags = empty_list(validated_data.pop('tags', []))
        ingredients_list = empty_list(validated_data.pop('ingredients', []))
        tags_already_exist = [tag for tag in instance.tags.all()]
        ingredients_already_exist = [ing for ing in instance.ingredients.all()]
        ingredients = [ing['ingredient'] for ing in ingredients_list]
        if tags_already_exist != tags:
            db = instance.tags.through.objects
            tags_set = set(tags + tags_already_exist)
            for tag in tags_set:
                if tag not in tags_already_exist:
                    db.create(recipe_id=instance.id, tag_id=tag.id)
                if tag not in tags:
                    db.filter(recipe_id=instance.id, tag_id=tag.id).delete()
        if ingredients_already_exist != ingredients:
            db = instance.ingredients.through.objects
            ingredients_set = set(ingredients + ingredients_already_exist)
            for ing in ingredients_set:
                if ing not in ingredients_already_exist:
                    ing_amount = [ingr for ingr in ingredients_list
                                  if ingr['ingredient'] == ing][0]['amount']
                    db.create(recipe_id=instance.id, ingredient_id=ing.id,
                              amount=ing_amount)
                if ing not in ingredients:
                    db.filter(recipe_id=instance.id,
                              ingredient_id=ing.id).delete()

        instance.refresh_from_db()

        instance.name = validated_data.pop('name', instance.name)
        instance.text = validated_data.pop('text', instance.text)
        instance.image = validated_data.pop('image', instance.image)
        instance.cooking_time = validated_data.pop(
            'cooking_time', instance.cooking_time)
        instance.save()
        return instance


class UserFollRecipeSerializer(UserSerializer):
    """Выдача списка подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'recipes',
            'recipes_count'
        ]

    def get_gs(self, obj):
        return Recipe.objects.filter(author=obj)

    def get_recipes(self, obj):
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', 5))
        return RecipeShoplistFavoriteSerializer(
            self.get_gs(obj)[:recipes_limit], many=True).data

    def get_recipes_count(self, obj):
        return self.get_gs(obj).count()
