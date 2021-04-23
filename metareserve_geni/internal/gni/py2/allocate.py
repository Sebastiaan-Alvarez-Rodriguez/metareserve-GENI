import argparse
import datetime
import socket
import sys

from geni.rspec import pg
import geni.util
import geni.aggregate.cloudlab

import allocate.generic as generic
from allocrequest import AllocRequest
import location.location as locutil

'''CLI module to start a cluster.'''

def get_context():
    return geni.util.loadContext()




def create_baremetal_node(name, img, hardware_type):
    node = pg.RawPC(name)
    node.disk_image = img
    node.hardware_type = hardware_type
    return node


def create_lan(nodes):
    lan = pg.LAN("lan")

    # create an interface for each node and add it to the lan
    for i, n in enumerate(nodes):
        iface = n.addInterface("if1")
        iface.component_id = "eth1"
        iface.addAddress(
            pg.IPv4Address("192.168.1.{}".format(i+1), "255.255.255.0"))
        lan.addInterface(iface)
    return lan


def create_request(allocrequest, with_lan):
    request = pg.Request()
    geni_nodes = []

    for node in allocrequest.list():
        geni_node = create_baremetal_node(node.name, node.img, node.hw_type)
        geni_nodes.append(geni_node)
        request.addResource(geni_node)

    # add lan to request
    if with_lan:
        lan = create_lan(geni_nodes)
        request.addResource(lan)
    return request


def _allocate_slice(ctx, slicename, expiration):
    '''Creates or renews a GENI slice. A slice is basically a sliver-holder. A sliver is a reservation. Slices and slivers all have expiration dates. We aim to keep those constant.
    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.'''
    state, date = generic.slice_create(ctx, slicename, expiration=expiration)
    if state == generic.CreationState.FAILED:
        print('Could not create (or renew) slice!')
        return None
    print('Slice created/renewed until date: {}.'.format(date))
    return date



def _allocate_sliver(ctx, slicename, allocrequest, location, with_lan=True, expiration=60*24*7, renew_exist=True, retries=5, retries_sleep=5, wait_ready=True, wait_sleep=15, wait_stop=60*10):
    '''Creates (or optionally renews) a sliver with a Ceph cluster. Requires an existing slice with given `slicename`.
    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        allocrequest (AllocRequest): Allocation Request object.
        location (geni location object): Physical cluster site. Picked site must support spawning images on raw hardware.
        with_lan (bool): If set, we declare that our spawned cluster must have an internal interconnect, name eth1.
        expiration: If `int` type, used as sliver expiration time in minutes from now. If `datetime` type, used as the expiration date.
        renew_exist (bool): If set, renews the sliver, setting the expiration date at `expiration` minutes from now.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.
        wait_ready (bool): If set, this function will block until the VM is ready.
        wait_sleep: Number of seconds to wait between ready-checks.
        wait_stop: Number of seconds before we give up on waiting for a ready-status. Stopping before being ready counts as a failure.

    Returns:
        A manifest on success, `None` on failure.
    '''
    if not lowercase_alpha(slicename):
        print('Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))
        return None

    request = create_request(allocrequest, with_lan)

    date = datetime_get(expiration)
    return sliver_create(ctx, slicename, request, location, date, renew_exist, retries, retries_sleep, wait_ready, wait_sleep, wait_stop)


def allocate(slicename, expiration, location, tmpoutloc=None):
    '''Allocates cluster. Note: Expects stdin to contain an AllocRequest in str form.
    Args:
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.
        slicename: Slice name.
        location: Location for sliver allocation.

    Returns:
        `True` on success, `False` otherwise. On success, also prints relevant connection info for the cluster.'''
    ctx = get_context()
    ar = AllocRequest.from_string(''.join(sys.stdin.readlines()))
    loc = locutil.location_get(location)

    date = _allocate_slice(ctx, slicename, expiration)
    if not date: # If we could not create slice, we failed.
        return False 

    manifest = _allocate_sliver(ctx, slicename, ar, loc, expiration=date)

    if manifest == None:
        return False
    infos = '\n'.join(str(info) for info in manifest.get_connect_info())
    print(infos)
    with open(tmpoutloc, 'w') as f:
        f.write(infos)
    return True


def subparser(subparsers):
    '''Register subparser modules'''
    allocateparser = subparsers.add_parser('allocate', help='Allocate nodes for a cluster directly on U.S. federal government clusters.')
    allocateparser.add_argument('time', metavar='time', help='Starts cluster for given amount of minutes if int given. Assumes date of format "%%Y-%%m-%%dT%%H:%%M:%%S" otherwise.')
    allocateparser.add_argument('-n', '--name', metavar='name', default='msparkceph', help='Name for slice on US resource (default="msparkceph")')
    allocateparser.add_argument('-l', '--location', metavar='location', nargs='?', default='cl-utah', const='cl-utah', help='Location of allocation (default="cl-utah", which is CloudLab, Utah site)')
    allocateparser.add_argument('--tmpoutloc', nargs='?', default=None, const=None, help=argparse.SUPPRESS)
    return [allocateparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'allocate'


def deploy(parsers, args):
    return allocate(args.name, args.time, args.location, args.tmpoutloc)