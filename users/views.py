from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from users.models import User
from users.serializers import UserUpdateSerializer


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
