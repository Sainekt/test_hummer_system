from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer
from phonenumbers import NumberParseException
from pages.validators import phone_number_validator, confirm_code_validator
from users.utils import create_user_or_confirm_cod
from django.core.exceptions import ValidationError
from users.models import UserConfirmCode
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'invite_code',)


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        try:
            data = phone_number_validator(value)
        except NumberParseException:
            raise serializers.ValidationError(
                'Введен не корректный номер телефона.')
        return data

    def create(self, validated_data):
        region_code, phone_number = validated_data['phone_number']
        create_user_or_confirm_cod(phone_number, region_code)
        validated_data['phone_number'] = (
            'Вам отправлен смс код потдверждения.'
            'введите ваш код подтверждения и номер телефона для получения'
            'токена по адресу /api/verify-sms/')
        return validated_data


class AuthTokenSerializers(serializers.Serializer):
    token = serializers.CharField()


class SMSCodeSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=4, min_length=4)
    phone_number = serializers.CharField(max_length=18)

    class Meta:
        model = User
        fields = (
            'phone_number', 'sms_code',
        )

    def validate_sms_code(self, value):
        try:
            confirm_code_validator(value)
        except ValidationError as error:
            raise serializers.ValidationError(error.message)
        return value

    def validate_phone_number(self, value):
        try:
            data = phone_number_validator(value)
        except NumberParseException:
            raise serializers.ValidationError(
                'Введен не корректный номер телефона.')
        return data

    def validate(self, attrs):
        data = super().validate(attrs)
        region_code, phone_number = data['phone_number']
        confirm_code = data['sms_code']
        user = User.objects.filter(phone_number=phone_number)
        if not user.exists():
            raise serializers.ValidationError('Не верный код подтверждения.')
        confirm_code_obj = UserConfirmCode.objects.filter(
            user=user.first(),
            confir_code=confirm_code
        )
        if not confirm_code_obj.exists():
            raise serializers.ValidationError('Не верный код подтверждения.')
        return data

    def create(self, validated_data):
        region_code, phone_number = validated_data['phone_number']
        user = get_object_or_404(User, phone_number=phone_number)
        token, created = Token.objects.get_or_create(user=user)
        validated_data['token'] = token
        return validated_data

    def to_representation(self, instance):
        return AuthTokenSerializers(instance).data