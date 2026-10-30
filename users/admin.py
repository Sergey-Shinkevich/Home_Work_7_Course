from django.contrib import admin

from users.models import Payments, User

# Регистрируем кастомного пользователя
admin.site.register(User)

# Регистрируем платежи
admin.site.register(Payments)
