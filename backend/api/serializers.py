import base64
from pprint import pprint

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from urllib3 import request

from api.serializers_fields import ImageBase64Field
from api.models import Tag, Ingredient, Recipe, IngredientsForRecipe
from users.serializers import UserSerializer

User = get_user_model()

class GetUser:

    def get_user(self):
        return self.context['request'].user

# class UserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField(read_only=True)
#     # avatar = serializers.SerializerMethodField() # Разобраться
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')
#
#     def get_is_subscribed(self, obj):
#         # print(obj)
#         # print(self.context["request"].user)
#         return obj in self.context["request"].user.follows.all()

# class ImageBase64Field(serializers.ImageField):
#     """Изображение в формате base 64."""
#
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#         return super().to_internal_value(data)


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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'amount',
        )
        # read_only_fields = ('id', 'amount')

    # def create(self, validated_data):
    #     ingredirnt_id = validated_data.pop('id')
    #     recipe = validated_data.pop('id')

class IngredientForRecipeGetSerializer(serializers.ModelSerializer):
    """Отображение ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(source='ingredient.measurement_unit')
# string replace to slug in future


    class Meta:
        model = IngredientsForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

class BaseRecipeSerializer(serializers.ModelSerializer):

    image = ImageBase64Field()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            # 'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]


class RecipeSerializer(BaseRecipeSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    # image = ImageBase64Field()
    # link = serializers.HyperlinkedIdentityField(view_name='recipe-detail')

    class Meta(BaseRecipeSerializer.Meta):
        # model = Recipe
        fields = (BaseRecipeSerializer.Meta.fields
        + [
            # 'id',
            # 'tags',
            'author',
            # 'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            # 'name',
            # 'image',
            # 'text',
            # 'cooking_time'
        ])

    def get_ingredients(self, obj):
        qs = IngredientsForRecipe.objects.filter(recipe=obj).all()
        return IngredientForRecipeGetSerializer(qs, many=True).data

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        return bool(obj in self.get_user().favorite_recipes.all())

    def get_is_in_shopping_cart(self, obj):
        return bool(obj in self.get_user().shop_list.all())


class RecipeCreateSerializer(BaseRecipeSerializer, GetUser):
    """Создание рецептов."""

    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientForRecipeCreateSerializer(many=True)

    class Meta(BaseRecipeSerializer.Meta):
        pass
        # fields = BaseRecipeSerializer.Meta.fields
        # fields += []

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data, author=self.get_user())
        for tag in tags:
            Recipe.tags.through.objects.create(recipe_id=recipe.id, tag_id=tag.id)
        for ingredient in ingredients:
            Recipe.ingredients.through.objects.create(
                recipe_id=recipe.id,
                ingredient_id=ingredient['ingredient'].id,
                amount=ingredient['amount'],
            )
        recipe.refresh_from_db()
        return recipe

    def update(self, instance, validated_data):
        tags_already_exist = [tag for tag in instance.tags.all()]
        ingredients_already_exist = [ing for ing in instance.ingredients.all()]
        tags = validated_data.pop('tags', [])
        ingredients_list = validated_data.pop('ingredients', [])
        ingredients = [ing['ingredient'] for ing in ingredients_list]
        # Добавить сортировку для проверки
        if tags_already_exist != tags:
            DB = instance.tags.through.objects
            tags_set = set(tags + tags_already_exist)
            for tag in tags_set:
                if tag not in tags_already_exist:
                    DB.create(recipe_id=instance.id, tag_id=tag.id)
                if tag not in tags:
                    DB.filter(recipe_id=instance.id, tag_id=tag.id).delete()
        if ingredients_already_exist != ingredients:
            DB = instance.ingredients.through.objects
            ingredients_set = set(ingredients + ingredients_already_exist)
            for ing in ingredients_set:
                if ing not in ingredients_already_exist:
                    ing_amount = [ingr for ingr in ingredients_list if ingr['ingredient'] == ing][0]['amount']
                    DB.create(recipe_id=instance.id, ingredient_id=ing.id, amount=ing_amount)
                if ing not in ingredients:
                    DB.filter(recipe_id=instance.id, ingredient_id=ing.id).delete()
        # Пилим дальше


