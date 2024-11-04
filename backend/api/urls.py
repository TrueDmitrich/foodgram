from django.urls import path, include
from rest_framework import routers

from users.views import AuthViewSet
from api import views

router = routers.DefaultRouter()
router.register('users', AuthViewSet)
router.register('tags', views.TagViewSet)
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]