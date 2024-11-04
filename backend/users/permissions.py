from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """Разрешения для пользователей."""

    NO_AUTH_ACTION_LIST = [
        'list',
        'retrieve',
        'create',
    ]
    AUTH_ACTION_LIST = (
        'avatar',
        'me',
        'subscriptions',
        'subscribe',
    )

    def has_permission(self, request, view):
        if (
            view.action in self.NO_AUTH_ACTION_LIST
            or request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return True
