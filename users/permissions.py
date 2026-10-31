from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором (состоит в группе 'Moderator')."""

    def has_permission(self, request, view):
        # Проверяем, авторизован ли пользователь и входит ли он в группу 'Moderator'
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='Moderator').exists()
    