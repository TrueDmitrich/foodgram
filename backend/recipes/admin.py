from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (
    Tag, Recipe, Ingredient, IngredientsForRecipe, User,
    Follows, UsersFavoriteRecipes, UsersShopRecipes)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'recipes_count')

    @admin.display(description='Число рецептов с тегом.')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Число рецептов с продуктом.')
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

    list_display = ('name', 'author', 'cooking_time', 'image')
    inlines = [IngredientsInline, TagsInline]
    search_fields = ('name', 'tags')
    list_filter = ('tags',)


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
class UserAdmin(UserAdmin):

    list_display = (
        'username', 'full_name', 'email', 'avatar',
        'recipes_count', 'followers_count', 'subscribers_count')
    list_filter = ('is_active',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [FollowsInline, FavoritesRecipesInline, ShopListInline]

    @admin.display(description='ФИО')
    def full_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    @admin.display(description='Число рецептов пользователя.')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Число подписок пользователя.')
    def followers_count(self, obj):
        return obj.followers.count()

    @admin.display(description='Число подписчиков пользователя.')
    def subscribers_count(self, obj):
        return obj.authors.count()
