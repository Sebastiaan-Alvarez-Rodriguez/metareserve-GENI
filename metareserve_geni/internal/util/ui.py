from internal.util.printer import *

# This file provides useful user interaction primitives.

def ask_int(question, minval=None, maxval=None):
    # Ask the user to provide an integer value, with optional min and max values
    while True:
        try:
            val = input(str(question)+' ').strip()
            val_cast = int(val)
            if minval != None and val_cast < minval:
                printe('Input is too small')
                continue
            if maxval != None and val_cast > maxval:
                printe('Input is too large')
                continue
            return val_cast
        except Exception as e:
            printe('Input "{0}" is not a number. Try again'.format(val))


def ask_bool(question, empty_ok=False):
    # Ask user for a boolean value. If `empty_ok` and no input given, False is returned.
    while True:
        val = input(str(question)+' ').strip().lower()
        if val in ('y', 'yes', 't', 'true'):
            return True
        elif val in ('n', 'no', 'f', 'false'):
            return False
        elif empty_ok and not any(val):
            return False
        else:
            printe('Input "{0}" could not be interpreted as a boolean. Try again'.format(val))

def ask_string(question, confirm=False, empty_ok=False):
    # Ask user for a string, possibly with confirmation
    while True:
        val = input(str(question)+' ').strip()
        if not empty_ok and not any(val):
            printe('You should not provide an empty string!')
        elif (confirm and ask_bool('Your choice: "{}". Are you absolutely sure this is correct?'.format(val))) or not confirm:
            return val

def ask_time(question):
    # Ask user for a string resembling [[hh:]mm:]ss
    while True:
        val = ask_string(question+' [[hh:]mm:]ss ')
        comps = val.split(':')
        complen = len(comps)
        if len(comps) > 3:
            printe('Provide time as [[hh:]mm:]ss. Try again.')
            continue
        if complen == 3: #We have hours, minutes and seconds
            if not comps[0].isnumeric():
                printe('Hours are not numeric. Try again.')
                continue
            del comps[0]
        if complen >= 2: #We have minutes and seconds
            if not comps[0].isnumeric():
                printe('Minutes are not numeric. Try again.')
                continue
            del comps[0]
        if complen >= 1: #We have seconds
            if comps[0].isnumeric():
                return val
            else:
                printe('Seconds are not numeric. Try again.')


def ask_pick(question, options: list):
    # Ask user to pick one of the displayed options.
    # Returns integer index of picked item.
    if len(options) == 0:
        raise RuntimeError('Cannot pick 1 option from 0 options!')
    while True:
        for idx, x in enumerate(options):
            print('[{}] - {}'.format(idx, x))
        try:
            val = input(str(question)+' ').strip()
            val_cast = int(val)
            if val_cast < 0:
                printe('Input is too small')
                continue
            if val_cast >= len(options):
                printe('Input is too large')
                continue
            return val_cast
        except Exception as e:
            printe('Input "{0}" is not a number. Try again'.format(val))

def ask_pick_multiple(question, options: list, minimal=1):
    # Like ask_pick(), ask users to pick an item.
    # Returns a sorted list of integer indices of picked items.
    if minimal < 0 or minimal > len(options):
        raise RuntimeError('Cannot pick {} options in a list of size {}'.format(minimal, len(options)))
    while True:
        for idx, x in enumerate(options):
            print('[{}] - {}'.format(idx, x))
        
        print(str(question))
        vals = input('Select min {} {} (select multiple as e.g. "1, 4", none by pressing enter) '.format(minimal, 'item' if minimal == 1 else 'items')).strip()
        if len(vals) == 0:
            if minimal == 0:
                return []
            else:
                printe('Pick at least {} {}'.format(minimal, 'item' if minimal == 1 else 'items'))

        status_ok = True
        returnlist = []
        for val in vals.split(','):
            try:
                val_cast = int(val)
                if val_cast < 0:
                    printe('Input {} is too small'.format(val_cast))
                    status_ok = False
                elif val_cast >= len(options):
                    printe('Input {} is too large'.format(val_cast))
                    status_ok = False
                else:
                    returnlist.append(val_cast)
            except Exception as e:
                printe('Input "{}" is not a number'.format(val))

        if status_ok:
            if len(returnlist) >= minimal:
                returnlist.sort()
                return returnlist
            else:
                printe('Picked less than {} options. Try again'.format(minimal))
        else:
            printe('There were errors. Try again.')