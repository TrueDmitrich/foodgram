from django.urls import path, include
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register('users', views.AuthViewSet, basename='users')
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
