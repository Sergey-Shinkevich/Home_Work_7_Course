from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class MaterialsTestCase(APITestCase):

    def setUp(self):
        """Создаем тестовые данные и пользователей с разными правами до тестов."""
        # 1. Создаем обычного пользователя (владелец контента)
        self.user = User.objects.create(email="user@test.com", password="testpassword123")

        # 2. Создаем пользователя-модератора и добавляем в группу 'Moderator'
        self.moderator_user = User.objects.create(email="moderator@test.com", password="testpassword123")
        moderator_group, _ = Group.objects.get_or_create(name="Moderator")
        self.moderator_user.groups.add(moderator_group)

        # 3. Создаем курс и урок, принадлежащие обычному пользователю
        self.course = Course.objects.create(
            name="Django REST Framework",
            description="Отличный курс по DRF с ссылкой на https://www.youtube.com/watch?v=123",
            owner=self.user,
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            name="Введение в DRF",
            description="Урок по настройке сериализаторов",
            video_url="https://www.youtube.com/watch?v=test",
            owner=self.user,
        )

    # --- ТЕСТЫ CRUD УРОКОВ ---

    def test_lesson_list(self):
        """Тест: просмотр списка уроков авторизованным пользователем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results", response.data)), 1)

    def test_lesson_retrieve(self):
        """Тест: просмотр детальной информации об уроке (владелец или модератор)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson-detail", args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), self.lesson.name)

    def test_lesson_create_by_regular_user(self):
        """Тест: создание урока обычным пользователем (успешно)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson-create")
        data = {
            "name": "Новый урок",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=valid",
            "course": self.course.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_by_moderator_forbidden(self):
        """Тест: модератору запрещено создавать уроки (~IsModerator)."""
        self.client.force_authenticate(user=self.moderator_user)
        url = reverse("materials:lesson-create")
        data = {
            "name": "Урок от модератора",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=valid",
            "course": self.course.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_by_owner_or_moderator(self):
        """Тест: обновление урока владельцем или модератором."""
        self.client.force_authenticate(user=self.moderator_user)
        url = reverse("materials:lesson-update", args=[self.lesson.id])
        data = {"name": "Обновлено модератором"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "Обновлено модератором")

    def test_lesson_destroy_by_owner(self):
        """Тест: удаление урока владельцем (успешно)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson-delete", args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_destroy_by_moderator_forbidden(self):
        """Тест: модератору запрещено удалять уроки (только владелец)."""
        self.client.force_authenticate(user=self.moderator_user)
        url = reverse("materials:lesson-delete", args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- ТЕСТЫ ВАЛИДАЦИИ И ПОДПИСОК ---

    def test_lesson_youtube_validation_failure(self):
        """Тест: валидатор блокирует сторонние ресурсы (не YouTube) в уроке."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:lesson-create")
        data = {
            "name": "Плохой урок",
            "description": "Описание",
            "video_url": "https://badsite.com/watch?v=hack",
            "course": self.course.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_toggle(self):
        """Тест: проверка создания и удаления подписки на курс (toggle-логика)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:subscription_toggle")
        data = {"course_id": self.course.id}

        # 1. Подписываемся
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # 2. Удаляем подписку при повторном запросе
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_is_subscribed_field(self):
        """Тест: проверка поля is_subscribed в сериализаторе курса."""
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, course=self.course)

        url = reverse("materials:courses-detail", args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("is_subscribed"))
