from rest_framework.filters import OrderingFilter
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from users.models import User, Payments
from users.serializers import UserUpdateSerializer, PaymentsSerializer


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
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_type')
    ordering_fields = ('payment_date',)
    ordering = ('-payment_date',)