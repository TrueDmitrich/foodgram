import base64
from pprint import pprint

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.serializers_fields import ImageBase64Field
from api.models import Tag, Ingredient, Recipe, IngredientsForRecipe
from users.serializers import UserSerializer

User = get_user_model()


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


class IngredientForRecipeSerializer(serializers.ModelSerializer):
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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = ImageBase64Field()
    # link = serializers.HyperlinkedIdentityField(view_name='recipe-detail')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        qs = IngredientsForRecipe.objects.filter(recipe=obj).all()
        return IngredientForRecipeSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        return bool(obj.is_favorited)

    def get_is_in_shopping_cart(self, obj):
        return bool(obj.is_in_shopping_cart)