from datetime import timedelta
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Периодическая задача: блокирует пользователей (is_active=False),
    которые не заходили в систему более одного месяца.
    """
    # Определяем порог: текущее время минус 30 дней
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, у которых:
    # 1. Аккаунт активен (is_active=True)
    # 2. last_login заполнен и меньше, чем месяц назад
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    )

    count = inactive_users.count()
    if count > 0:
        # Блокируем их массово одним запросом
        inactive_users.update(is_active=False)
        print(f"Заблокировано неактивных пользователей: {count}")
    else:
        print("Нет пользователей для блокировки.")