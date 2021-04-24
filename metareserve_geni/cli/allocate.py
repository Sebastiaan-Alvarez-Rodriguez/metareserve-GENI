import argparse
import datetime

import internal.gni.py2bridge
from internal.util.printer import *
import internal.util.fs as fs
import internal.util.location as loc
import internal.util.ui as ui
from reservation import GENINode, GENIReservationRequest


'''CLI module to start a cluster.'''


def _cached(response, cached_val):
    return response if response else cached_val


def _check_time(time_amount):
    try:
        integer = int(obj)
        return integer < 7200
    except Exception as e:
        user_date =  datetime.datetime.strptime(obj, '%Y-%m-%dT%H:%M:%S')
        time_delta = user_date - datetime.datetime.now()
        return time_delta.total_seconds()/60 < 7200


def build_request_interactive(time_amount, node_amount, location, slicename):
    print('Building request interactive. If you want to use a config file, use the "-c/--conf" option.')
    
    r = GENIReservationRequest(node_amount, time_amount, location, slicename)

    default_name = 'node{}'
    cached_hwtype = None
    cached_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'
    picked_names = []
    for idx in range(node_amount):
        print('Processing node {}/{}'.format(idx+1, node_amount))
        
        while True:
            name_question = '\tname (lowercase) [{}]:'.format(default_name.format(idx))
            reply_name = _cached(ui.ask_string(name_question, empty_ok=True), default_name.format(idx)).lower()
            if reply_name not in picked_names:
                break
            print('Name already picked ({}). Pick a unique name'.format(','.join(picked_names)))

        hw_question = '\thwtype' + (' [{}]:'.format(cached_hwtype) if cached_hwtype else ':')
        cached_hw_type = _cached(ui.ask_string(hw_question, empty_ok=True), cached_hwtype) if cached_hwtype else ui.ask_string(hw_question)
        
        img_question = '\timage [{}]:'.format(cached_image)
        cached_image = _cached(ui.ask_string(img_question, empty_ok=True), cached_image)
        
        r.add(GENINode(reply_name, cached_hwtype, cached_image))

    print('Reservation profile complete.')
    if ui.ask_bool('Save profile? [N]:', empty_ok=True):
        while True:
            cached_profilename = 'new_profile'
            profile_name_question = 'Profile name (lowercase) [{}]:'.format(cached_profilename)
            cached_profilename = _cached(ui.ask_string(profile_name_question, empty_ok=True), cached_profilename).lowercase()+'.cfg'

            os.makedirs(loc.profiledir(), exist_ok=True)
            if os.path.isfile(os.path.join(loc.profiledir(), cached_profilename)):
                if not ui.ask_bool(os.path.join(loc.profiledir(), cached_profilename)+' already exists. Override:'):
                    continue
            with open(os.path.join(loc.profiledir(), cached_profilename), 'w') as f:
                f.write(str(r))
            break

    return r


def check_and_allocate(time_amount, node_amount, location, slicename, conf):
    if not _check_time(time_amount):
        printw('''Provided time "{0}" is too far away in the future. Max allocation time is 7199 minutes (date={1}).
To hold a reservation for longer, periodically rerun this command to renew the reservation.
Set date to {1}'''.format(
            time_amount,
            datetime.datetime.strftime(datetime.datetime.now()+datetime.timedelta(minutes=7199), '%Y-%m-%dT%H:%M:%S'),
        ))

        time_amount = datetime.datetime.now()+datetime.timedelta(minutes=7199)
    if conf and os.path.isfile(conf):
        with open(conf, 'r') as f:
            reservation_request.from_string('\n'.join(f.readlines()))
    else:
        reservation_request = build_request_interactive(time_amount, node_amount)
    py2bridge.allocate(expiration, reservation_request)



def print_profiles(name=None):
    '''Prints known profiles.
    Args:
        name (optional str): If set, prints contents of named config.'''
    print('Profiles are stored at {}. found:'.format(loc.profiledir()))
    if fs.isdir(loc.profiledir()):
        for x in fs.ls(loc.profiledir(), only_files=True, full_paths=True):
            print(fs.basename(x))
    print('')
    if name != '_':
        name = name.lower()
        if not name.endswith('.cfg'):
            name += '.cfg'
        if not fs.isfile(loc.profiledir(), name):
            printe('No profile named "{}" available.'.format(name))
            return
        with open(fs.join(loc.profiledir(), name)) as f:
            print('\n'.join(f.readlines()))


def subparser(subparsers):
    '''Register subparser modules'''
    allocateparser = subparsers.add_parser('allocate', help='Allocate nodes for a cluster directly on U.S. federal government clusters.')
    allocateparser.add_argument('-t', '--time', default='120', metavar='time', help='Reserves cluster for given amount of minutes if int given. Assumes date of format "%%Y-%%m-%%dT%%H:%%M:%%S" otherwise (default=120)')
    allocateparser.add_argument('-a', '--amount', default=1, type=int, metavar='nodes', help='Amount of nodes to reserve.')
    allocateparser.add_argument('-l', '--location', metavar='location', nargs='?', default='cl-utah', const='cl-utah', help='Location of allocation (default="cl-utah", which is CloudLab, Utah site)')
    allocateparser.add_argument('-n', '--name', metavar='name', default='metareserve', help='Name for slice on US resource (default="metareserve")')

    allocateparser.add_argument('-c', '--conf', metavar='name', default=None, help='Read the request information from a named profile instead of providing it manually.')
    allocateparser.add_argument('-cl', '--conf-list', dest='conf_list', nargs='?', default='', const='_', help='Print stored reservation profiles. If a name is given, prints given profile.')
    # subsubparsers = allocateparser.add_subparsers(help='Sub2commands', dest='subcommand')
    return [allocateparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'allocate'


def deploy(parsers, args):
    if args.conf_list:
        print_profiles(args.conf_list)
        return True
    return check_and_allocate(args.time, args.amount, args.location, args.name, args.conf)