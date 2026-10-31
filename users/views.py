from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payments, User
from users.permissions import IsUserSelf
from users.serializers import PaymentsSerializer, UserPublicSerializer, UserSerializer, UserUpdateSerializer


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]  # Редактировать может только себя

    def get_object(self):
        return self.request.user


class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_type")
    ordering_fields = ("payment_date",)
    ordering = ("-payment_date",)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Динамически выбираем сериализатор в зависимости от действия и владельца."""
        if self.action == "retrieve":
            # Если это запрос детальной информации, проверяем объект
            user_obj = self.get_object()
            if user_obj != self.request.user:
                # Чужой профиль — показываем урезанные данные
                return UserPublicSerializer
        # Для своего профиля, списка, создания и обновления — полный сериализатор
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            # Регистрация доступна всем
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Изменять и удалять можно только свой собственный профиль
            permission_classes = [IsAuthenticated, IsUserSelf]
        else:
            # Просмотр списка и детальной информации — любому авторизованному
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
