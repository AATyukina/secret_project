import string
import random
from django.conf import settings

LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = string.punctuation


def generate_access_key() -> str:
    printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'
    printable = list(printable)
    random.shuffle(printable)

    return ''.join(random.choices(printable, k=settings.ACCESS_KEY_LENGTH))
