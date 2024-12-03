import random
from time import sleep
import logging

from django.contrib.auth import get_user_model

from .models import UserConfirmCode

User = get_user_model()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DICTIONARY_REFERAL_CODE = (
    'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890'
)
DICTIONARY_CONFIRM_CODE = '0123456789'


def check_unique(referal_code) -> str | bool:
    try:
        User.objects.get(referal_code=referal_code)
    except User.DoesNotExist:
        return referal_code
    return False


def get_code(dictionary, length) -> str:
    length = length
    code = False
    if dictionary == DICTIONARY_CONFIRM_CODE:
        code = ''.join(random.choice(dictionary) for _ in range(length))
    while not code:
        code = check_unique(
            ''.join(random.choice(dictionary) for _ in range(length))
        )
    return code


def sending_sms(confirm_code):
    sleep(2)

    logger.info(f'Ваш смс код подтверждения:{confirm_code}'
                '\nНикому не сообщайте его.')


def create_user_or_confirm_cod(phone_number, region=None):
    user = User.objects.filter(phone_number=phone_number)
    confir_code = get_code(DICTIONARY_CONFIRM_CODE, 4)
    if not user.exists():
        referal_code = get_code(DICTIONARY_REFERAL_CODE, 6)
        user = User.objects.create(
            phone_number=phone_number,
            referal_code=referal_code,
            region=region,)
        user.save()
        UserConfirmCode.objects.create(
            user=user,
            confir_code=confir_code,
        ).save()
        sending_sms(confir_code)
        return
    user = user[0]
    confirm_code_obj = UserConfirmCode.objects.filter(user=user)
    if not confirm_code_obj.exists():
        UserConfirmCode.objects.create(
            user=user,
            confir_code=confir_code,
        ).save()
        return
    confirm_code_obj = confirm_code_obj[0]
    confirm_code_obj.confir_code = confir_code
    confirm_code_obj.save()
    sending_sms(confir_code)
