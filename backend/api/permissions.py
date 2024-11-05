from rest_framework import permissions


class RecipesPermission(permissions.BasePermission):
    """Разрешения для рецептов."""

    def has_permission(self, request, view):
        if (
            (request.method in permissions.SAFE_METHODS)
            and (view.action != "download_shopping_cart")
            or request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (
            view.action not in ("update", "partial_update", "destroy")
            or request.user == obj.author
        ):
            return True
        return False


class UserPermission(permissions.BasePermission):
    """Разрешения для пользователей."""

    AUTH_ACTION_LIST = (
        "avatar",
        "me",
        "subscriptions",
        "subscribe",
    )

    def has_permission(self, request, view):
        if (
            view.action not in self.AUTH_ACTION_LIST
            or request.user.is_authenticated
        ):
            return True
        return False
