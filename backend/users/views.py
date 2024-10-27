from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer


class AuthViewSet(UserViewSet):
    """Дополненный viewset из Djoser."""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
