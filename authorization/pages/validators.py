from django.core.exceptions import ValidationError
from phonenumbers import parse, NumberParseException


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
