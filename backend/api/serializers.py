from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Tag, Ingredient, Recipe
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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(IngredientSerializer):
    amount = serializers.SerializerMethodField()

    # def get_amount(self, obj):
    #     return obj.


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

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

    def get_is_favorited(self, obj):
        return self.data['is_favorited']

    def get_is_in_shopping_cart(self, obj):
        return self.data['is_in_shopping_cart']