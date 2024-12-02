from rest_framework import status, views, viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from users.models import UserConfirmCode
from .serializers import UserSerializer, SMSCodeSerializer, PhoneNumberSerializer
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthPhoneNumberViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RequestSMSCodeView(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = PhoneNumberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()


class VerifySMSCodeView(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = SMSCodeSerializer

