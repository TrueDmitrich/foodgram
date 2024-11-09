from rest_framework import permissions

#
# class AuthorOrReadOnly(permissions.BasePermission):
#     """Разрешения для User и Recipe API."""
#
#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or obj.author == request.user)

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
        return bool(
            request.method in permissions.SAFE_METHODS
            and (view.action not in self.AUTH_ACTIONS)
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        def user_or_recipe(obj):
            return obj.author if hasattr(obj, 'author') else obj

        return bool(
            view.action in ('retrieve', 'get_link')
            or view.action in self.AUTH_ACTIONS
            or user_or_recipe(obj) == request.user
        )
