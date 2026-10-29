from django.urls import path
from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import PaymentsViewSet, UserUpdateAPIView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentsViewSet, basename="payments")


urlpatterns = [
    path("update/", UserUpdateAPIView.as_view(), name="user-update"),
] + router.urls
