from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.views import UserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pages.validators import invite_code_validator

from .permissions import IsUserOrReadOnly
from .serializers import (PhoneNumberSerializer, SMSCodeSerializer,
                          WriteInviteCodeSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    @action(
        ['patch'], detail=False, url_path='me/invite_code',
        permission_classes=[IsUserOrReadOnly]
    )
    def write_invire_code(self, request, *args, **kwargs):
        serializer = WriteInviteCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite_code = serializer.data['invite_code']
        try:
            invite_code = invite_code_validator(
                invite_code, User, request.user)
        except ValidationError as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        request.user.invite_code = invite_code
        request.user.save()
        return Response(
            {'invite_code': invite_code}, status=status.HTTP_200_OK)


class RequestSMSCodeView(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = PhoneNumberSerializer
    permission_classes = [AllowAny]


class VerifySMSCodeView(generics.CreateAPIView, viewsets.GenericViewSet):
    serializer_class = SMSCodeSerializer
    permission_classes = [AllowAny]
