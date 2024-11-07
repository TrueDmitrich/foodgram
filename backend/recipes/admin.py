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

    @admin.display(description='Рецептов с тегом.')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецептов с продуктом.')
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
        'recipe_image', 'tags_list', 'ingredients_list')
    exclude = ('tags', 'ingredients')
    inlines = [IngredientsInline, TagsInline]
    search_fields = ('name', 'tags')
    list_filter = ('tags',)

    @admin.display(description='Фото')
    def recipe_image(self, recipe):
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}"'
                             f' width="150px" height="100px" />')

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return ', '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        return ', '.join(tag.name for tag in recipe.ingredients.all())


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

    @admin.display(description='ФИО')
    def full_name(self, user):
        return user.first_name + ' ' + user.last_name

    @admin.display(description='Рецептов.')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок.')
    def followers_count(self, user):
        return user.followers.count()

    @admin.display(description='Подписчиков.')
    def subscribers_count(self, user):
        return user.authors.count()
