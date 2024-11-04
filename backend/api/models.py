from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F


# Здесь чтоб не мучиться с цикличностью
class User(AbstractUser):
    """Переопределенный User."""

    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    avatar = models.ImageField('Фото', upload_to='media/users', blank=True)
    follows = models.ManyToManyField(
        'User', verbose_name='Подписки', symmetrical=False, blank=True,
        through='UserFollows', related_name='+')
    favorite_recipes = models.ManyToManyField(
        'Recipe', verbose_name='Избранные рецепты',
        related_name='+', blank=True)
    shop_list = models.ManyToManyField('Recipe', related_name='+', blank=True)

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = "email"

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.id} {self.username}.'


class UserFollows(models.Model):
    """Подписки на пользователей."""

    # user подписан на follow
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='folws')
    follow = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='who_follow')

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follow'], name='unique_follow'),
            models.CheckConstraint(
                name='ban_self_follow',
                check=~models.Q(user=F('follow'))
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.follow}.'


class Tag(models.Model):
    """Теги для рецептов."""

    name = models.CharField('Название тега', max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta(AbstractUser.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты для рецептов."""

    name = models.CharField('Наименование', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.TextField('Имя рецепта', max_length=256)
    image = models.ImageField('Фото', upload_to='media/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsForRecipe', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах:',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'], name='unique_author_rectipe')
        ]

    def __str__(self):
        return f'{self.id} {self.name}'


class IngredientsForRecipe(models.Model):
    """Список ингредиентов и их количества для рецепта."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Для рецепта')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        'Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_rectipes_ingr')
        ]

    def __str__(self):
        return f'{self.ingredient.name} для {self.recipe.name[:10]}'
