from django.contrib import admin
from users.models import User, Payments

# Регистрируем кастомного пользователя
admin.site.register(User)

# Регистрируем платежи
admin.site.register(Payments)