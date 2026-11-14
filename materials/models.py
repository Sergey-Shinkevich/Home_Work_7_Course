from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название курса")
    preview = models.ImageField(
        upload_to="materials/courses/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)",
    )
    description = models.TextField(verbose_name="Описание курса")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=150, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    preview = models.ImageField(
        upload_to="materials/lessons/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)",
    )
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="subscriptions",
    )

    def __str__(self):
        return f"{self.user} подписан на {self.course}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")


class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name="Курс", null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, verbose_name="Урок", null=True, blank=True)
    amount = models.PositiveIntegerField(verbose_name="Сумма оплаты")
    payment_id = models.CharField(max_length=255, verbose_name="ID платежа в Stripe", null=True, blank=True)
    payment_url = models.URLField(max_length=500, verbose_name="Ссылка на оплату", null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.course or self.lesson} ({self.amount})"
