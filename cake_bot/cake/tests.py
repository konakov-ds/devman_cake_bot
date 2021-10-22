from django.test import TestCase
import re
# Create your tests here.
phone_number_valid = re.findall(r'\+?[\d]{1}[\d]{10}', '+71231231212')
print(phone_number_valid)