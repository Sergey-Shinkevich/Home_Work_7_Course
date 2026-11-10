from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


# Viewset для Курсов (CRUD через ModelViewSet)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def perform_create(self, serializer):
        """Автоматически привязываем создаваемый курс к текущему пользователю."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == 'create':
            # Создавать могут только авторизованные пользователи, которые НЕ являются модераторами
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактировать может модератор или владелец
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            # Удалять может ТОЛЬКО владелец (модераторам удалять запрещено)
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр списка и детальной информации доступен авторизованным
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


# Generic-классы для Уроков (все 5 операций CRUD)


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]  # Модераторам создание запрещено (позже добавим проверку owner)

    def perform_create(self, serializer):
        """Автоматически привязываем создаваемый урок к текущему пользователю."""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Доступно всем авторизованным (включая модераторов)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]  # Модераторам удаление запрещено, только владелец!
