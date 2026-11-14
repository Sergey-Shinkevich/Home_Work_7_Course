from drf_spectacular.utils import OpenApiParameter, extend_schema  # Импортируем для документации
from rest_framework import generics, serializers, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Payment, Subscription
from materials.paginators import MaterialsPaginator
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    PaymentSerializer,
    SubscriptionRequestSerializer,
    SubscriptionResponseSerializer,
)
from materials.services import (
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_stripe_session_status,
)
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
        responses={200: SubscriptionResponseSerializer},
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


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создание платежа в Stripe",
        description="Создает запись о платеже в базе данных, регистрирует продукт и сессию в Stripe и возвращает URL для оплаты.",
    )
    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        # Получаем название курса или урока для продукта в Stripe
        product_name = (
            payment.course.name if payment.course else (payment.lesson.name if payment.lesson else "Оплата материала")
        )

        # 1. Создаем продукт в Stripe
        product_id = create_stripe_product(product_name)

        # 2. Создаем цену (сумма умножается на 100 в сервисной функции)
        price_id = create_stripe_price(payment.amount, product_id)

        # 3. Создаем сессию оплаты
        session_id, payment_url = create_stripe_session(price_id)

        # Сохраняем данные от Stripe в нашу модель
        payment.payment_id = session_id
        payment.payment_url = payment_url
        payment.save()


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверка статуса платежа в Stripe",
        description="Запрашивает актуальный статус сессии из Stripe по payment_id и возвращает его.",
    )
    def get(self, request, pk, *kwargs):
        # Находим платеж в нашей базе данных по первичному ключу (id)
        payment = get_object_or_404(Payment, id=pk, user=request.user)

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
