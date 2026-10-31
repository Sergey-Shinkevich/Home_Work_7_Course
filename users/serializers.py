from rest_framework import serializers

from users.models import Payments, User


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("email", "phone", "city", "avatar")


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        # Добавили 'password' в fields:
        fields = ("id", "email", "phone", "city", "avatar", "payments", "password")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance