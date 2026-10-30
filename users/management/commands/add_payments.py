from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payments, User


class Command(BaseCommand):
    help = "Создает тестовые платежи в базе данных"

    def handle(self, *args, **options):
        # Удаляем старые платежи, чтобы не плодить дубликаты при каждом запуске
        Payments.objects.all().delete()

        # Создаем тестового пользователя, если его еще нет
        user, created = User.objects.get_or_create(
            email="test@sky.pro",
            defaults={
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("12345")
            user.save()

        # Создаем тестовый курс, если его еще нет
        course, _ = Course.objects.get_or_create(
            name="Python разработчик", defaults={"description": "Курс по изучению Django и DRF"}
        )

        # Создаем тестовый платеж за курс
        payment = Payments.objects.create(
            user=user, paid_course=course, payment_amount=15000.00, payment_type=Payments.CASH
        )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создан тестовый платеж для {user.email} за курс "{course.name}"!')
        )
