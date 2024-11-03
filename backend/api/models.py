from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F



# Здесь чтоб не мучиться с цикличностью
class User(AbstractUser):
    """Переопределенный User."""

    # username_validator = UnicodeUsernameValidator()

    # username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    avatar = models.ImageField(upload_to='media/users', blank=True)
    follows = models.ManyToManyField('User', symmetrical=False, blank=True, through='UserFollows', related_name='+')
    favorite_recipes = models.ManyToManyField('Recipe', related_name='+', blank=True)
    shop_list = models.ManyToManyField('Recipe', related_name='+', blank=True)

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = "email"

    # class Meta(AbstractUser.Meta):
    #     constraints = [


class UserFollows(models.Model):
    # user подписан на follow
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folws' )
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name='who_follow')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follow'], name='unique_follow'),
            models.CheckConstraint(
                name='ban_self_follow',
                check=~models.Q(user=F('follow'))
            )
        ]



class Tag(models.Model):
    """Теги для рецептов."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты для рецептов."""

    name = models.CharField(max_length=50)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.TextField(max_length=256)
    image = models.ImageField(upload_to='media/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsForRecipe')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField(verbose_name='Cooking time min:',
        validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'name'], name='unique_author_rectipe')
        ]

    def __str__(self):
        return self.name


class IngredientsForRecipe(models.Model):
    """Список ингредиентов и их количества для рецепта."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_rectipes_ingr')
        ]

    def __str__(self):
        return f'{self.ingredient.name} для {self.recipe.name[:10]}'


class U(models.Model):

    user = models.CharField(max_length=50)
    follows = models.ManyToManyField('U', related_name='fol')
    fav_rec = models.ManyToManyField('Rec', related_name='fav')
    shop_list = models.ManyToManyField('Rec', related_name='shop')
    def __str__(self):
        return self.user

class Rec(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


# class FavoriteRecipe(UserField):
#     """Избранные рецепты."""
#
#     favorite_recipes = models.ManyToManyField(Recipe, related_name='favorite_recipes', blank=True)
#
# class ShopList(UserField):
#     """Покупки."""

    shop_list = models.ManyToManyField(Recipe, related_name='shop_list', blank=True)



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