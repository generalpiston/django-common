import re

from django.core.exceptions import ValidationError

def validate_zipcode(value):
    if value > 99999 or value < 0:
        raise ValidationError(u'%d is not a valid zipcode.' % value)

def validate_city(value):
    if not re.match("^[a-zA-Z\s]+$", value):
        raise ValidationError(u'%s is not a valid city name.' % value)
