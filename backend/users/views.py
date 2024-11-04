from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import UserPermission
from users.serializers import UserSerializer, UserImageSerializer
from api.serializers import UserFollRecipeSerializer


User = get_user_model()


class AuthViewSet(UserViewSet):
    """Дополненный viewset из Djoser."""

    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

    @action(methods=['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserImageSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user
        foll = [u.follow for u in user.folws.all().select_related('follow')]
        data = self.paginate_queryset(UserFollRecipeSerializer(
            foll, context={'request': request}, many=True
        ).data)
        return self.get_paginated_response(data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        obj = self.get_object()
        db = request.user.follows.through.objects
        # Не стал похожее объединять. Вроде того не стоит.
        if request.method == 'POST':
            if (
                db.filter(user=request.user, follow=obj,).exists()
                or obj == request.user
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            db.create(
                user=request.user,
                follow=obj,
            )
            return Response(
                data=UserFollRecipeSerializer(
                    self.get_object(), context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not (
                db.filter(user=request.user, follow=obj,).exists()
                or obj == request.user
            ):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            db.filter(
                user=request.user.id,
                follow=obj.id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
