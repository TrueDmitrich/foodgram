from django.contrib import admin

from api.models import Tag, Recipe, Ingredient, IngredientsForRecipe
from api.views import User

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}

# admin.site.register(Tag)
# admin.site.register(Recipe)
admin.site.register(User)
admin.site.register(Ingredient)


class RecipeInline(admin.TabularInline):

    model = IngredientsForRecipe

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = [RecipeInline]


# class FollowsInline(admin.TabularInline):
#
#     model = UserFollows
#     fk_name = 'user'
#
#
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#
#     inlines = [FollowsInline]
#     exclude = ['follows']

