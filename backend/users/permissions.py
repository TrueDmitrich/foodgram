from rest_framework import permissions


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.author == request.user

class UserPermission(permissions.BasePermission):
    """Разрешения для рецептов."""

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
        if (view.action in self.NO_AUTH_ACTION_LIST
                or request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # if (view.action in self.AUTH_ACTION_LIST)
        #     or request.user.is_authenticated)
        # ):
        #     return True
        return True
    # def has_permission(self, request, view):
    #     if (view.action in self.ACTION_TO_AUTH) and request.user.is_authenticated:
    #         return True
    #     return False
    #
    # def has_object_permission(self, request, view, obj):
    #     return True
