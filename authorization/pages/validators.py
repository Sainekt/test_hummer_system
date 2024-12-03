from django.core.exceptions import ValidationError
from phonenumbers import NumberParseException, parse


def phone_number_validator(phone, region_code=None) -> tuple:
    try:
        number = parse(phone, region_code)
    except NumberParseException:
        raise ValidationError('Введен не корректный номер телефона.')
    phone_number = f'+{number.country_code}{number.national_number}'
    return (region_code, phone_number)


def confirm_code_validator(value) -> str:
    if not value:
        raise ValidationError('Поле не может быть пустым.')
    if not value.isdigit():
        raise ValidationError('Код должен состоять из 4 цифр.')
    if len(value) != 4:
        raise ValidationError('Введите 4-ех значный код.')
    return value


def invite_code_validator(value, model, obj) -> str:
    if value and len(value) != 6:
        raise ValidationError('код должен состоять из 6 символов')
    user_invite_code = model.objects.filter(referal_code=value)
    if value and not user_invite_code.exists():
        raise ValidationError('Код приглашения не существует.')
    if obj.invite_code and obj.invite_code != value:
        raise ValidationError(
            'Код приглашения можно активировать только 1 раз.')
    if value == obj.referal_code:
        raise ValidationError('Нельзя использовать свой код приглашения.')
    return value


def email_validator(email, user, model) -> str:
    if user.email != email:
        users = model.objects.filter(email=email)
        none_emais = [i for i in users if i.email is None]
        if len(none_emais) == len(users):
            return email
        raise ValidationError('Адрес электронной почты уже существует.')
    return email
