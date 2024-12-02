from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer
from phonenumbers import NumberParseException
from pages.validators import phone_number_validator, confirm_code_validator
from users.utils import create_user_or_confirm_cod
from django.core.exceptions import ValidationError


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


class SMSCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    sms_code = serializers.CharField()

    def validate_sms_code(self, value):
        try:
            confirm_code_validator(value)
        except ValidationError as error:
            raise serializers.ValidationError(error.message)

    def create(self, validated_data):
        return validated_data