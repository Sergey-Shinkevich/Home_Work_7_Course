from rest_framework import serializers
from users.models import User, Payments


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("email", "phone", "city", "avatar")

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"