from rest_framework import permissions


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.author == request.user

class OwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        print('alo')
        return (
            request.method in permissions.SAFE_METHODS
            )

    def has_object_permission(self, request, view, obj):
        print('alo2')
        return (
            request.method == 'GET'
            or obj == request.user
        )