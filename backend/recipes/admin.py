from django.contrib import admin

from recipes.models import (
    Tag, Recipe, Ingredient, IngredientsForRecipe, User,
    UsersFollows, UsersFavoriteRecipes, UsersShopRecipes)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


class IngredientsInline(admin.TabularInline):

    model = IngredientsForRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = [IngredientsInline]
    search_fields = ('name', 'tags')
    list_filter = ('tags',)


class FollowsInline(admin.TabularInline):

    model = UsersFollows
    fk_name = 'user'
    verbose_name_plural = 'Подписан на:'


class FavoritesRecipesInline(admin.TabularInline):

    model = UsersFavoriteRecipes
    verbose_name_plural = 'Избранные рецепты:'


class ShopListInline(admin.TabularInline):

    model = UsersShopRecipes
    verbose_name_plural = 'Список рецептов к покупке:'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    inlines = [FollowsInline, FavoritesRecipesInline, ShopListInline]
    search_fields = ('username', 'first_name', 'last_name', 'email')
