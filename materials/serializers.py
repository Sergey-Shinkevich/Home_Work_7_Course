from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field  # <--- Импортируем декоратор

from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [YouTubeValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):

    @extend_schema_field(serializers.IntegerField)
    def get_count_lessons(self, obj):
        return obj.lessons.count()

    count_lessons = serializers.SerializerMethodField()

    lessons = LessonSerializer(many=True, read_only=True)


    @extend_schema_field(serializers.BooleanField)
    def get_is_subscribed(self, obj):
        # Получаем текущего пользователя из контекста запроса
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Проверяем, существует ли подписка этого пользователя на данный курс
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"
        validators = [YouTubeValidator(field="description")]

# Сериализатор для ответа кастомного эндпоинта подписки чтобы Swagger красиво отображал ответ
class SubscriptionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

# Сериализатор для входящих данных (что передаем в теле запроса)
class SubscriptionRequestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(help_text="ID курса для подписки/отписки")