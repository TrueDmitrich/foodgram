from rest_framework import permissions


class RecipesPermission(permissions.BasePermission):
    """Разрешения для рецептов."""

    NO_AUTH_ACTION_LIST = [
        'get_link',
        'list',
        'retrieve'
    ]
    AUTH_ACTION_LIST = [
        'download_shopping_cart',
        'shopping_cart',
        'favorite',
    ]

    def has_permission(self, request, view):
        if (
            view.action in self.NO_AUTH_ACTION_LIST
            or request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (view.action in (self.NO_AUTH_ACTION_LIST + self.AUTH_ACTION_LIST)
                or request.user == obj.author):
            return True
        return False
