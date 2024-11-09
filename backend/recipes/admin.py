from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjoserUserAdmin
from django.utils.safestring import mark_safe

from recipes.models import (
    Tag, Recipe, Ingredient, IngredientsForRecipe, User,
    Follows, UsersFavoriteRecipes, UsersShopRecipes)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'recipes_count')

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


class IngredientsInline(admin.TabularInline):

    model = IngredientsForRecipe
    min_num = 1


class TagsInline(admin.TabularInline):

    model = Recipe.tags.through
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'name', 'author', 'cooking_time',
        'recipe_image', 'tags_list', 'ingredients_list', 'cooking_time')
    exclude = ('tags', 'ingredients')
    inlines = [IngredientsInline, TagsInline]
    search_fields = ('name', 'tags')
    list_filter = ('tags', 'author__username')

    @mark_safe
    @admin.display(description='Фото')
    def recipe_image(self, recipe):
        if recipe.image:
            return (f'<img src="{recipe.image.url}"'
                    ' width="150px" height="100px" />')
        return '-'

    @mark_safe
    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        return '<br>'.join(
            '{} {} {}'.format(
            note.ingredient.name, note.amount, note.ingredient.measurement_unit
        ) for note in recipe.ingredientsforrecipe.all().select_related(
            'ingredient'
        ))


class FollowsInline(admin.TabularInline):

    model = Follows
    fk_name = 'user'
    verbose_name_plural = 'Подписан на:'


class FavoritesRecipesInline(admin.TabularInline):

    model = UsersFavoriteRecipes
    verbose_name_plural = 'Избранные рецепты:'


class ShopListInline(admin.TabularInline):

    model = UsersShopRecipes
    verbose_name_plural = 'Список рецептов к покупке:'


@admin.register(User)
class UserAdmin(DjoserUserAdmin):

    list_display = (
        'username', 'full_name', 'email', 'avatar_image',
        'recipes_count', 'followers_count', 'subscribers_count')
    list_filter = ('is_active',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [FollowsInline, FavoritesRecipesInline, ShopListInline]

    @admin.display(description='Фото')
    def avatar_image(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}"'
                ' width="150px" height="100px" />')
        return 'Не установлено.'

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def followers_count(self, user):
        return user.followers.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.authors.count()


class AbstractUserRecipeAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')


@admin.register(UsersFavoriteRecipes)
class UsersFavoriteRecipesAdmin(AbstractUserRecipeAdmin):
    """Избранные рецепты пользователей."""


@admin.register(UsersShopRecipes)
class UsersShopRecipesAdmin(AbstractUserRecipeAdmin):
    """Рецепты для корзины пользователей."""


@admin.register(Follows)
class Follows(admin.ModelAdmin):
    """Подписки пользователей."""

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user__username', 'author__username')
