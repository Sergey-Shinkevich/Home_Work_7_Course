from rest_framework import generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter # Импортируем для документации

from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPaginator
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionRequestSerializer, \
    SubscriptionResponseSerializer
from users.permissions import IsModerator, IsOwner


# Viewset для Курсов (CRUD через ModelViewSet)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = MaterialsPaginator

    def perform_create(self, serializer):
        """Автоматически привязываем создаваемый курс к текущему пользователю."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == "create":
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


# Generic-классы для Уроков (все 5 операций CRUD)
class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [
        IsAuthenticated,
        ~IsModerator,
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPaginator


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
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]

class SubscriptionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Управление подпиской на курс",
        description="Создает подписку, если ее не было, или удаляет, если она уже существовала.",
        request=SubscriptionRequestSerializer,
        responses={200: SubscriptionResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message})