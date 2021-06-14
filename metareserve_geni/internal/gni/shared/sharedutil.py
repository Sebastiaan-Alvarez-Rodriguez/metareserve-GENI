import datetime
import re

def lowercase_alpha(string):
    '''Returns `True` iff `string` only contains lowercase letters, numbers, and '-'. Returns `False` otherwise.'''
    return re.match('^[a-z0-9\-]+$', string) != None


def datetime_get(obj):
    '''Converts number strings and strings to datetimes.'''
    if isinstance(obj, datetime.datetime):
        return obj
    try:
        integer = int(obj)
        return (datetime.datetime.now() + datetime.timedelta(minutes=integer))
    except Exception as e:
        return datetime.datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S')
