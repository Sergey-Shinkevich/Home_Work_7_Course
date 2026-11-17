from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Фоновая задача для отправки уведомлений подписчикам об обновлении курса.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    # Находим всех подписчиков именно этого курса
    subscriptions = Subscription.objects.filter(course=course).select_related('user')

    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipient_list:
        return

    subject = f'Обновление материалов курса: {course.name}'
    message = (
        f'Здравствуйте!\n\n'
        f'Материалы по курсу "{course.name}" были обновлены. '
        f'Заходите на платформу, чтобы ознакомиться с изменениями.'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )