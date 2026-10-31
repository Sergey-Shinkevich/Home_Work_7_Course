from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator  # Наш пермишен модератора


# Viewset для Курсов (CRUD через ModelViewSet)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            # Создавать могут только авторизованные (модераторам нельзя — можно добавить проверку или оставить IsAuthenticated, но на уровне логики создания мы защитим это позже)
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            # Удалять модераторам тоже нельзя
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'retrieve', 'list']:
            # Просматривать и редактировать могут авторизованные (включая модераторов)
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


# Generic-классы для Уроков (все 5 операций CRUD)

class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Модераторам создание запрещено (позже добавим проверку owner)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Доступно всем авторизованным (включая модераторов)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Доступно всем авторизованным (включая модераторов)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Модераторы могут редактировать любые уроки


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]  # Модераторам удаление запрещено