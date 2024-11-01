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
from users.serializers import UserSerializer

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
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            self.perform_update(serializer)
            # if not serializer.is_valid():
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # serializer.save(data=request.data)
            # Допилить ответ через юзера наверн
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(SUCCESS_DELETE_AVATAR, status=status.HTTP_200_OK)





    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().me(request)

