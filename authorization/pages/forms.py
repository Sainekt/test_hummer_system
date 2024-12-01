from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField
from phonenumbers import country_code_for_region, length_of_geographical_area_code, parse


class PhoneLoginForm(forms.Form):
    phone_number = SplitPhoneNumberField(region='RU')

    def clean(self):
        form_region_code = self.data['phone_number_0']
        form_phone_number = self.data['phone_number_1']
        number = parse(form_phone_number, form_region_code)
        phone_number = f'+{number.country_code}{number.national_number}'
        return (form_region_code, phone_number)


class ConfirmCodeForm(forms.Form):
    confirm_code = forms.CharField(
        label='Проверочный код',
        max_length=4,
        help_text='Введите код из смс',
        # error_messages='Неверный код!',
        )
