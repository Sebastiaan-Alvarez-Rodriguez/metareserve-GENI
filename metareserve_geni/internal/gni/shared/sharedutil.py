import datetime
import re

def lowercase_alpha(string):
    '''Returns `True` iff `string` only contains lowercase letters, `False` otherwise. Any other characters, e.g. `_` and `9` will not match.'''
    return re.match('^[a-z]+$', string) != None



def datetime_get(obj):
    '''Converts number strings and strings to datetimes.'''
    if isinstance(obj, datetime.datetime):
        return obj
    try:
        integer = int(obj)
        return (datetime.datetime.now() + datetime.timedelta(minutes=integer))
    except Exception as e:
        return datetime.datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S')


def datetime_str(obj):
    '''Converts a datetime to string.'''
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        raise RuntimeError('Cannot accept ints as datetime objects')
    if isinstance(obj, datetime.datetime):
        return datetime.datetime.strftime(obj, '%Y-%m-%dT%H:%M:%S')
