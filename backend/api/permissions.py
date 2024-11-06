from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Разрешения для User и Recipe API."""

    AUTH_ACTIONS = (
        'favorite',
        'shopping_cart',
        'download_shopping_cart',
        'create',

        'subscriptions',
        'subscribe',
        'me'
    )

    def has_permission(self, request, view):
        if (
            (request.method in permissions.SAFE_METHODS
                and view.action not in self.AUTH_ACTIONS)
            or request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        def user_or_recipe(obj):
            if hasattr(obj, 'author'):
                return obj.author
            return obj

        if (
            view.action in ('retrieve', 'get_link')
            or view.action in self.AUTH_ACTIONS
            or user_or_recipe(obj) == request.user
        ):
            return True
        return False
