from rest_framework import permissions


class IsUAu(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
    def has_object_permission(self, request, view, obj):
        return True

class RecipesPermission(permissions.BasePermission):
    """Разрешения для рецептов."""

    ACTION_LIST = [
        'get_link',
        'download_shopping_cart',
        'shopping_cart',
        'favorite',
    ]

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            or view.action in self.ACTION_LIST
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (request.method == "GET"
            or request.user == obj.author
            or view.action in self.ACTION_LIST
        ):
            return True
        return False