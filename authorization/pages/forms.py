from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField
from phonenumbers import parse, NumberParseException
from django.core.exceptions import ValidationError
from users.models import UserConfirmCode
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


class PhoneLoginForm(forms.Form):
    phone_number = SplitPhoneNumberField(region='RU')

    def clean(self) -> tuple:
        form_region_code = self.data['phone_number_0']
        form_phone_number = self.data['phone_number_1']
        try:
            number = parse(form_phone_number, form_region_code)
        except NumberParseException:
            raise ValidationError('Введен не корректный номер телефона.')
        phone_number = f'+{number.country_code}{number.national_number}'
        return (form_region_code, phone_number)


class ConfirmCodeForm(forms.Form):
    confirm_code = forms.CharField(
        label='Проверочный код',
        max_length=4,
        help_text='Введите код из смс',
        )
    phone_number = forms.CharField(widget=forms.HiddenInput())

    def clean_confirm_code(self) -> str:
        value = self.cleaned_data.get('confirm_code')
        if not value:
            raise ValidationError('Поле не может быть пустым.')
        if not value.isdigit():
            raise ValidationError('Код должен состоять из 4 цифр.')
        if len(value) != 4:
            raise ValidationError('Введите 4-ех значный код.')
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
        if self.user.email != email:
            if not User.objects.filter(email=email).exists():
                return email
            raise ValidationError('Адрес электронной почты уже существует.')
        return email

    def clean_invite_code(self) -> str:
        value = self.cleaned_data.get('invite_code')
        if value and len(value) != 6:
            raise ValidationError('код должен состоять из 6 символов')
        user_invite_code = User.objects.filter(referal_code=value)
        if value and not user_invite_code.exists():
            raise ValidationError('Код приглашения не существует.')
        if self.user.invite_code:
            raise ValidationError(
                'Код приглашения можно активировать только 1 раз.')
        if value == self.user.referal_code:
            raise ValidationError('Нельзя использовать свой код приглашения.')
        return value
