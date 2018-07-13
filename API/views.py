from django.contrib import auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from keys.models import Key
from .serializers import KeySerializer, UserSerializer

class KeyDetail(APIView):
    """Retrieve a Key instance"""

    def get(self,request):
        key = Key.objects.filter(user__pk=request.user.pk).first()
        serializer = KeySerializer(key)
        return Response(serializer.data)

class UserList(APIView):
    """Retrieve a Key instance"""

    permission_classes = (IsAdminUser,)

    def get(self,request):
        user_model = auth.get_user_model()
        users = user_model.objects.all()
        serializer = UserSerializer(users,many=True)
        return Response(serializer.data)
