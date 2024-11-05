from django.contrib import admin

from api.models import Tag, Recipe, Ingredient, IngredientsForRecipe
from api.views import User


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):

    model = IngredientsForRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = [IngredientsInline]
    search_fields = ('user__username', 'name')
    # Фильтр по тегам


class FollowsInline(admin.TabularInline):

    model = User.follows.through
    fk_name = 'user'
    verbose_name_plural = 'Подписан на:'


class FavoritesRecipesInline(admin.TabularInline):

    model = User.favorite_recipes.through
    verbose_name_plural = 'Избранные рецепты:'


class ShopListInline(admin.TabularInline):

    model = User.shop_list.through
    verbose_name_plural = 'Список рецептов к покупке:'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    inlines = [FollowsInline, FavoritesRecipesInline, ShopListInline]
    exclude = ['follows', 'favorite_recipes', 'shop_list']
    search_fields = ('username', 'first_name', 'last_name', 'email')
