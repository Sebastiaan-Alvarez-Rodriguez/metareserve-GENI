import argparse
import datetime

import internal.gni.py2bridge as py2bridge
from internal.util.printer import *
import internal.util.fs as fs
import internal.util.location as loc
import internal.util.ui as ui
from reservation import GENINode, GENIReservationProfile, GENIReservationRequest


'''CLI module to start a cluster.'''


def _cached(response, cached_val):
    return response if response else cached_val




def _check_time(minutes):
        return minutes < 7200

def build_profile_interactive(node_amount):
    '''Builds a `GENIReservationProfile` by asking questions to the user.
    Args:
        node_amount (int): Amount of nodes to add in our profile.

    Returns:
        `GENIReservationProfile` with `node_amount` nodes.'''
    print('Building request interactively. If you want to use a config file, use the "-c/--conf" option.')
    
    profile = GENIReservationProfile()

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
        cached_hwtype = _cached(ui.ask_string(hw_question, empty_ok=True), cached_hwtype) if cached_hwtype else ui.ask_string(hw_question)
        
        img_question = '\timage [{}]:'.format(cached_image)
        cached_image = _cached(ui.ask_string(img_question, empty_ok=True), cached_image)
        
        profile.add(GENINode(reply_name, cached_hwtype, cached_image))

    print('Reservation profile complete.')
    if ui.ask_bool('Save profile? [N]:', empty_ok=True):
        while True:
            cached_profilename = 'new_profile'
            profile_name_question = 'Profile name (lowercase) [{}]:'.format(cached_profilename)
            cached_profilename = _cached(ui.ask_string(profile_name_question, empty_ok=True), cached_profilename).lower()+'.cfg'

            fs.mkdir(loc.profiledir(), exist_ok=True)
            if fs.isfile(fs.join(loc.profiledir(), cached_profilename)):
                if not ui.ask_bool(fs.join(loc.profiledir(), cached_profilename)+' already exists. Override:'):
                    continue
            with open(fs.join(loc.profiledir(), cached_profilename), 'w') as f:
                f.write(str(profile))
            print('Wrote config at location: {}'.format(fs.join(loc.profiledir(), cached_profilename)))
            break
    prints('Resrvation profile creation success.')
    return profile


def check_and_allocate(time_alloc, node_amount, location, slicename, conf):
    if not _check_time(time_alloc):
        printw('''Provided time "{}" is too far away in the future. Max allocation time is 7199 minutes.
To hold a reservation for longer, periodically rerun this command to renew the reservation.
Set allocation time to 7199'''.format(time_alloc))
        time_alloc = 7199
    if conf:
        if not conf.endswith('.cfg'):
            conf += '.cfg'
        if fs.isfile(loc.profiledir(), conf):
            with open(fs.join(loc.profiledir(), conf), 'r') as f:
                reservation_request = GENIReservationRequest(time_alloc, location, slicename, GENIReservationProfile.from_string(''.join(f.readlines())))
        else:
            printe('Profile config named "{}" does not exist.'.format(conf))
            return False
    else:
        reservation_request = GENIReservationRequest(time_alloc, location, slicename, build_profile_interactive(node_amount))
    nodes = py2bridge.allocate(time_alloc, reservation_request)

    if not nodes:
        printe('There was an error during allocation.')
        return False
    print('node_id,node_name,ip_local,ip_public,port,extra_info')
    for x in nodes:
        print(str(x))
    prints('Reservation success')
    return True


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
        print('Contents of {}:'.format(name))
        with open(fs.join(loc.profiledir(), name)) as f:
            print(''.join(f.readlines()))


def subparser(subparsers):
    '''Register subparser modules'''
    allocateparser = subparsers.add_parser('allocate', help='Allocate nodes for a cluster directly on U.S. federal government clusters.')
    allocateparser.add_argument('-t', '--time', default=120, metavar='minutes', type=int, help='Reserves cluster for given amount of minutes (default=120).')
    allocateparser.add_argument('-a', '--amount', default=1, type=int, metavar='nodes', help='Amount of nodes to reserve.')
    allocateparser.add_argument('-l', '--location', metavar='location', nargs='?', default='cl-utah', const='cl-utah', help='Location of allocation (default="cl-utah", which is CloudLab, Utah site)')
    allocateparser.add_argument('-n', '--name', metavar='name', default='metareserve', help='Name for slice on US resource (default="metareserve")')

    allocateparser.add_argument('-c', '--conf', metavar='name', default=None, help='Read the request information from a named profile instead of providing it manually. Replaces the need for `amount` option.')
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