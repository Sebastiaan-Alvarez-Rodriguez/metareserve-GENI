import argparse
import datetime

import internal.gni.py2bridge
from internal.util.printer import *

'''CLI module to start a cluster.'''


def _check_time(time_amount):
    try:
        integer = int(obj)
        return integer < 7200
    except Exception as e:
        user_date =  datetime.datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S')
        time_delta = user_date - datetime.datetime.now()
        return time_delta.total_seconds()/60 < 7200


def check_and_allocate(slicename, time_amount, location):
    if not _check_time(time_amount):
        printw('''Provided time "{0}" is too far away in the future. Max allocation time is 7199 minutes (date={1}).
To hold a reservation for longer, periodically rerun this command to renew the reservation.
Set date to {1}'''.format(
            time_amount,
            datetime.datetime.strftime(datetime.datetime.now()+datetime.timedelta(minutes=7199), '%Y-%m-%dT%H:%M:%S'),
        ))

        time_amount = datetime.datetime.now()+datetime.timedelta(minutes=7199)
    py2bridge.allocate(expiration, reservation_request)


def subparser(subparsers):
    '''Register subparser modules'''
    allocateparser = subparsers.add_parser('allocate', help='Allocate nodes for a cluster directly on U.S. federal government clusters.')
    allocateparser.add_argument('time', metavar='time', help='Starts cluster for given amount of minutes if int given. Assumes date of format "%%Y-%%m-%%dT%%H:%%M:%%S" otherwise.')
    allocateparser.add_argument('-n', '--name', metavar='name', default='metareserve', help='Name for slice on US resource (default="metareserve")')
    allocateparser.add_argument('-l', '--location', metavar='location', nargs='?', default='cl-utah', const='cl-utah', help='Location of allocation (default="cl-utah", which is CloudLab, Utah site)')
    allocateparser.add_argument('-c', '--conf', help='Read the request information from a file instead of providing it manually.')
    # subsubparsers = allocateparser.add_subparsers(help='Sub2commands', dest='subcommand')
    return [allocateparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'allocate'


def deploy(parsers, args):
    return check_and_allocate(args.name, args.time, args.location)