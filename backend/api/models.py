from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F


# Здесь чтоб не мучиться с цикличностью
class User(AbstractUser):
    """Переопределенный User."""

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    avatar = models.ImageField(upload_to='media/users', blank=True)
    follows = models.ManyToManyField('User', symmetrical=False, blank=True, through='UserFollows', related_name='+')
    favorite_recipes = models.ManyToManyField('Recipe', related_name='+', blank=True)
    shop_list = models.ManyToManyField('Recipe', related_name='+', blank=True)

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = "email"


class UserFollows(models.Model):
    """Подписки на пользователей."""

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
