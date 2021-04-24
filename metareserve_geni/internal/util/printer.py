from enum import Enum
import os
import builtins

# The greater purpose of (functions in) this file is to convert strings to colored strings, which helps navigating the commandline interface.

def print(*args, **kwargs):
    # Overridden print function to always flush.
    # We need this practically everywhere when using multithreading with prints across machines.
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

def printc(string, color, **kwargs):
    # Print given text with given color
    print(format(string, color), **kwargs)

def prints(string, color=Color.GRN, **kwargs):
    # Print given success text
    print('[SUCCESS] {}'.format(format(string, color)), **kwargs)

def printw(string, color=Color.YEL, **kwargs):
    # Print given warning text
    print('[WARNING] {}'.format(format(string, color)), **kwargs)

def printe(string, color=Color.RED, **kwargs):
    # Print given error text
    print('[ERROR] {}'.format(format(string, color)), **kwargs)


def format(string, color):
    # Format a string with a color
    if os.name == 'posix':
        return '{}{}{}'.format(color.value, string, Color.CLR.value)
    return string