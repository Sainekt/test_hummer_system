from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from phonenumbers import NumberParseException
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from pages.validators import (confirm_code_validator, email_validator,
                              phone_number_validator)
from users.models import UserConfirmCode
from users.utils import create_user_or_confirm_cod

User = get_user_model()


class UserSerializer(UserSerializer):
    invite_code = serializers.ReadOnlyField()
    referal_code = serializers.ReadOnlyField()
    invited = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'referal_code',
                  'invite_code',
                  'invited',
                  )

    def get_invited(self, obj):
        invited = User.objects.filter(invite_code=obj.referal_code)
        data = [i.phone_number for i in invited]
        return data

    def validate_email(self, value):
        if not (request := self.context.get('request')):
            raise ValidationError('Вы не авторизованы.')
        validate_email = email_validator(value, request.user, User)
        return validate_email


class WriteInviteCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('invite_code',)


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    region_code = serializers.CharField(
        max_length=5,
        min_length=1,
        required=False
    )

    def validate(self, attrs):
        data = super().validate(attrs)
        phone_number = data['phone_number']
        region_code = data['region_code']
        try:
            phone_number_validator(phone_number, region_code)
        except NumberParseException:
            raise serializers.ValidationError(
                'Введен не корректный номер телефона.')
        return data

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        region_code = validated_data['region_code']
        if not region_code:
            region_code = validated_data['region_code']
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
