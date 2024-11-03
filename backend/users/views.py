from pprint import pprint

from django.contrib.auth import get_user_model
from django.contrib.messages import SUCCESS
from django.shortcuts import render
from djoser.views import UserViewSet
from pyexpat.errors import messages
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.admin import FavoritesRecipesInline
from users.permissions import OwnerOrReadOnly
from users.serializers import UserSerializer, UserImageSerializer
from api.serializers import UserFollRecipeSerializer

User = get_user_model()

SUCCESS_DELETE_AVATAR = 'Аватар успешно удален'


class AuthViewSet(UserViewSet):
    """Дополненный viewset из Djoser."""

    serializer_class = UserSerializer
    pagination_class = pagination.LimitOffsetPagination


# Try to remove
    def get_queryset(self):
        print(1)
        return User.objects.all()

    # Доделать
    @action(methods=['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request):
        # уБРАТЬ в пермишенс
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if request.method == 'PUT':
            serializer = UserImageSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            # if not serializer.is_valid():
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # serializer.save(data=request.data)
            # Допилить ответ через юзера наверн
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().me(request)

    @action(methods=['get'], detail=False)
    def subscriptions(self):
        user = self.request.user
        foll = user.followers.all()
        return Response(UserFollRecipeSerializer(
            foll, context={'request': self.request}
        ).data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        obj = self.get_object()
        DB = request.user.follows.through.objects
        if request.method == 'POST':
            DB.create(
                user=request.user,
                follow=obj,
            )
        return Response(
            data=UserFollRecipeSerializer(self.get_object(), context={'request': request}).data,
            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            DB.filter(
                user=request.user.id,
                follow=obj.id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

# http://localhost/api/users/{id}/subscribe/
# http://localhost/api/users/subscriptions/
