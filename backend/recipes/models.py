from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F

from recipes.constants import (
    MIN_VALUE_TO_RECIPE_COOK, MIN_VALUE_TO_INGREDIENT_AMOUNT)


class User(AbstractUser):
    """Переопределенный User."""

    username = models.CharField(
        'Ник',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    avatar = models.ImageField('Фото', upload_to='media/users', blank=True)

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    USERNAME_FIELD = 'email'

    class Meta(AbstractUser.Meta):
        ordering = ('username', 'email')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.id} {self.username}.'


class AbstractUserRecipe(models.Model):
    """Общие свойства для связей user-recipe."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        abstract = True
        ordering = ('user',)
        default_related_name = '%(class)ss'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique_user_recipe'),)


class UsersFavoriteRecipes(AbstractUserRecipe):
    """Избранные рецепты."""

    class Meta(AbstractUserRecipe.Meta):
        verbose_name = 'Избранный рецепт пользователя.'
        verbose_name_plural = 'Избранные рецепты пользователей.'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}.'


class UsersShopRecipes(AbstractUserRecipe):
    """Рецепты в списке покупок."""

    class Meta(AbstractUserRecipe.Meta):
        verbose_name = 'Рецепт для корзины пользователя.'
        verbose_name_plural = 'Рецепты для корзины пользователей.'

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}.'


class Follows(models.Model):
    """Подписки пользователей."""

    # user подписан на author
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='followers')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='authors')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_follow'),
            models.CheckConstraint(
                name='ban_self_follow',
                check=~models.Q(user=F('author'))
            )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'


class Tag(models.Model):
    """Теги для рецептов."""

    name = models.CharField('Название', max_length=50, unique=True)
    slug = models.SlugField('Уникальное имя', max_length=50, unique=True)

    class Meta(AbstractUser.Meta):
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Продукты для рецептов."""

    name = models.CharField('Наименование', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.TextField('Имя рецепта', max_length=256)
    image = models.ImageField('Фото', upload_to='media/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsForRecipe', verbose_name='Продукты')
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах:',
        validators=(MinValueValidator(MIN_VALUE_TO_RECIPE_COOK),))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name'), name='unique_author_recipe'),
        )

    def __str__(self):
        return f'{self.name} {self.author.username} '


class IngredientsForRecipe(models.Model):
    """Список продуктов и их количества для рецепта."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Для рецепта')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Продукт')
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(MIN_VALUE_TO_INGREDIENT_AMOUNT),))

    class Meta:
        ordering = ('recipe',)
        default_related_name = 'ingredientsforrecipe'
        verbose_name = 'Продукт для рецепта'
        verbose_name_plural = 'Продукты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_rectipes_ingr')
        ]

    def __str__(self):
        return f'{self.ingredient.name} для {self.recipe.name[:10]}'
