from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.serializers import UserSerializer
from users.models import Payments, User
from users.serializers import PaymentsSerializer, UserUpdateSerializer


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

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
    serializer_class = UserSerializer

    def get_permissions(self):
        # Если пользователь регистрируется (метод POST), разрешаем всем (AllowAny)
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            # Остальные действия (просмотр списка, профиля, удаление) требуют авторизации
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]