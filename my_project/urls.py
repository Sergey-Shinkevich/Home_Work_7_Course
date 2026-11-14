from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("materials.urls", namespace="materials")),
    path("users/", include("users.urls", namespace="users")),
    # Эндпоинт для скачивания сырой схемы OpenAPI в формате JSON/YAML
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI (интерактивная документация):
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # ReDoc (альтернативный красивый интерфейс документации):
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
