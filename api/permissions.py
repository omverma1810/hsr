from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission class to allow only authenticated admin users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsSuperAdmin(permissions.BasePermission):
    """Permission class to allow only super admin users."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser and
            request.user.role == 'Super Admin'
        )
