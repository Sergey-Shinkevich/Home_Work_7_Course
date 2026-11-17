from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Payments, User
from users.permissions import IsUserSelf
from users.serializers import PaymentsSerializer, UserPublicSerializer, UserSerializer, UserUpdateSerializer
from users.services import create_stripe_price, create_stripe_product, create_stripe_session, get_stripe_session_status


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
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создание платежа в Stripe",
        description="Создает запись о платеже в БД, регистрирует продукт, цену и сессию в Stripe и возвращает URL для оплаты.",
    )
    def perform_create(self, serializer):
        """При создании платежа автоматически привязываем текущего пользователя
        и генерируем сессию/ссылку на оплату в Stripe."""

        # Сохраняем платеж, привязывая к текущему пользователю
        payment = serializer.save(user=self.request.user)

        # Получаем название курса или урока для продукта в Stripe
        product_name = (
            payment.paid_course.name
            if payment.paid_course
            else (payment.paid_lesson.name if payment.paid_lesson else "Оплата материала")
        )

        # 1. Создаем продукт в Stripe
        product_id = create_stripe_product(product_name)

        # 2. Создаем цену (сумма платежа)
        price_id = create_stripe_price(payment.payment_amount, product_id)

        # 3. Создаем сессию оплаты
        session_id, payment_url = create_stripe_session(price_id)

        # Сохраняем данные от Stripe в модель
        payment.payment_id = session_id
        payment.payment_url = payment_url
        payment.save()

    @extend_schema(
        summary="Проверка статуса платежа в Stripe",
        description="Запрашивает актуальный статус сессии из Stripe по payment_id и возвращает его.",
    )
    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        # Находим платеж по id и текущему пользователю
        payment = get_object_or_404(Payments, id=pk, user=request.user)

        if not payment.payment_id:
            return Response({"error": "У этого платежа нет payment_id"}, status=400)

        # Получаем данные из Stripe
        stripe_info = get_stripe_session_status(payment.payment_id)

        return Response(
            {
                "payment_id": payment.payment_id,
                "stripe_status": stripe_info.get("status"),
                "payment_status": stripe_info.get("payment_status"),
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Динамически выбираем сериализатор в зависимости от действия и владельца."""
        if self.action == "retrieve":
            # Для генератора документации возвращаем стандартный сериализатор
            if getattr(self, "swagger_fake_view", False):
                return UserSerializer

            # Проверяем pk из URL без вызова self.get_object()
            pk = self.kwargs.get("pk")
            if self.request and self.request.user.is_authenticated and pk:
                # Если запрашивают чужой профиль — показываем урезанные данные
                if str(self.request.user.pk) != str(pk):
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

