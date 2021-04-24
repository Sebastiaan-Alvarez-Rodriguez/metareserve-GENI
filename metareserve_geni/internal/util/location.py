
'''Global locations we use.'''

import os

def storedir():
    return os.path.join(os.getenv('HOME'), '.metareserve', 'metareserve_geni')

def profiledir():
    return os.path.join(storedir(), 'profiles')