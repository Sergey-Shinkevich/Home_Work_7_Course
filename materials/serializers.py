from rest_framework import serializers
from materials.validators import YouTubeValidator
from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [
            YouTubeValidator(field='video_url')
        ]

class CourseSerializer(serializers.ModelSerializer):
    count_lessons = serializers.SerializerMethodField()

    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = "__all__"
        validators = [
            YouTubeValidator(field='description')
        ]