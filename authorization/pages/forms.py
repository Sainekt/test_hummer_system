from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from phonenumber_field.formfields import SplitPhoneNumberField

from users.models import UserConfirmCode

from .validators import (confirm_code_validator, email_validator,
                         invite_code_validator, phone_number_validator)

User = get_user_model()


class PhoneLoginForm(forms.Form):
    phone_number = SplitPhoneNumberField(region='RU')

    def clean(self) -> tuple:
        form_region_code = self.data['phone_number_0']
        form_phone_number = self.data['phone_number_1']
        region_code, phone_number = phone_number_validator(
            form_phone_number, form_region_code)
        return (region_code, phone_number)


class ConfirmCodeForm(forms.Form):
    confirm_code = forms.CharField(
        label='Проверочный код',
        max_length=4,
        help_text='Введите код из смс',
        )
    phone_number = forms.CharField(widget=forms.HiddenInput())

    def clean_confirm_code(self) -> str:
        value = self.cleaned_data.get('confirm_code')
        value = confirm_code_validator(value)
        return value

    def clean(self) -> dict:
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        confirm_code = cleaned_data.get('confirm_code')
        if not phone_number:
            raise ValidationError('Номер телефона не передан.')
        user = get_object_or_404(User, phone_number=phone_number)
        confirm_obj = get_object_or_404(UserConfirmCode, user=user)
        if confirm_obj.confir_code != confirm_code:
            raise ValidationError('Неправильный код.')
        cleaned_data['user'] = user
        return cleaned_data


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'invite_code',)

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        clean_email = email_validator(email, self.user, User)
        return clean_email

    def clean_invite_code(self) -> str:
        value = self.cleaned_data.get('invite_code')
        clean_value = invite_code_validator(value, User, self.user)
        return clean_value
