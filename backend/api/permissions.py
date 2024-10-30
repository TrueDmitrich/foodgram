from rest_framework import permissions


class IsUAu(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
    def has_object_permission(self, request, view, obj):
        return True