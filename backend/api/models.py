from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.models import AuthUser


# Здесь чтоб не мучиться с цикличностью



class User(AuthUser):
    """Переопределенный User."""

    # avatar = models.ImageField(upload_to='media/users', blank=True)
    follows = models.ManyToManyField('User', symmetrical=False, blank=True)
    favorite_recipes = models.ManyToManyField('Recipe', blank=True)
    shop_list = models.ManyToManyField('Recipe', related_name='shop_set', blank=True)

# class UserFollows(models.Model):
#     # user подписан на follow
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows')
#     follow = models.ForeignKey(User, on_delete=models.CASCADE)


class Tag(models.Model):
    """Теги для рецептов."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты для рецептов."""

    name = models.CharField(max_length=50)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='media/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsForRecipe')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class IngredientsForRecipe(models.Model):
    """Список ингредиентов и их количества для рецепта."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.recipe.name[:10]} {self.ingredient.name} {self.amount} {self.ingredient.measurement_unit} '


# class UserField(models.Model):
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
#
# class Follow(UserField):
#     """Подписки, избранные рецепты и список для покупок пользователя."""
#
#     follows = models.ForeignKey(User, related_name='follows', on_delete=models.CASCADE)
#
#
# class FavoriteRecipe(UserField):
#     """Избранные рецепты."""
#
#     favorite_recipes = models.ManyToManyField(Recipe, related_name='favorite_recipes', blank=True)
#
# class ShopList(UserField):
#     """Покупки."""
#
#     shop_list = models.ManyToManyField(Recipe, related_name='shop_list', blank=True)



# class TRecipe(models.Model):
#     name = models.CharField(max_length=100)
#
# class TUser(models.Model):
#     name = models.CharField(max_length=100)
#     favorite_recipes = models.ManyToManyField(TRecipe, blank=True)
#     shop_list = models.ManyToManyField(TRecipe, related_name='asdf', blank=True)
#
# TRecipe.objects.create(name='R1')

#
# class TFavRec(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, related_name='favorite_recipes',)
#     favorite_recipes = models.ForeignKey(TRecipe,  blank=True, on_delete=models.CASCADE)
#
# class TShop(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, related_name='shop_list')
#     shop_list = models.ForeignKey(TRecipe,  blank=True, on_delete=models.CASCADE)