from django.test import TestCase
import re
from datetime import datetime
# Create your tests here.
phone_number_valid = re.findall(r'\+?[\d]{1}[\d]{10}', '+71231231212')
print(phone_number_valid)
time = '23.10.2021 | 17:00'


def validate_delivery_time(time):
    try:
        time = datetime.strptime(time, '%d.%m.%Y | %H:%M')
        return time
    except Exception:
        return False
time = validate_delivery_time(time)
print(validate_delivery_time(time))

now = datetime.now()
delay = time - now
print(delay.days)