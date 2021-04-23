# The greater purpose of (functions in) this file is
# to convert strings to colored strings, which helps
# navigating the commandline interface


from enum import Enum
import os
import builtins

# Overridden print function to always flush.
# We need this practically everywhere when using ssh.
def print(*args, **kwargs):
    kwargs['flush'] = True
    return builtins.print(*args, **kwargs)


class Color(Enum):
    '''An enum to specify what color you want your text to be'''
    RED = '\033[1;31m'
    GRN = '\033[1;32m'
    YEL = '\033[1;33m'
    BLU = '\033[1;34m'
    PRP = '\033[1;35m'
    CAN = '\033[1;36m'
    CLR = '\033[0m'

# Print given text with given color
def printc(string, color, **kwargs):
    print(format(string, color), **kwargs)

# Print given success text
def prints(string, color=Color.GRN, **kwargs):
    print('[SUCCESS] {}'.format(format(string, color)), **kwargs)

# Print given warning text
def printw(string, color=Color.YEL, **kwargs):
    print('[WARNING] {}'.format(format(string, color)), **kwargs)


# Print given error text
def printe(string, color=Color.RED, **kwargs):
    print('[ERROR] {}'.format(format(string, color)), **kwargs)


# Format a string with a color
def format(string, color):
    if os.name == 'posix':
        return '{}{}{}'.format(color.value, string, Color.CLR.value)
    return string