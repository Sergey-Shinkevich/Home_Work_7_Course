from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [YouTubeValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    count_lessons = serializers.SerializerMethodField()

    lessons = LessonSerializer(many=True, read_only=True)

    # Добавляем поле для признака подписки
    is_subscribed = serializers.SerializerMethodField()

    def get_count_lessons(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        # Получаем текущего пользователя из контекста запроса
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Проверяем, существует ли подписка этого пользователя на данный курс
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = "__all__"
        validators = [YouTubeValidator(field="description")]
