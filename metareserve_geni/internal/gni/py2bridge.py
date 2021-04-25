import metareserve
import os
import subprocess
import tempfile

from internal.gni.shared.connectinfo import RawConnectInfo as _RawConnectInfo
import internal.gni.shared.sharedutil as _sharedutil
from internal.gni.shared.allocrequest import AllocRequest as _AllocRequest
import internal.util.fs as fs
from internal.util.printer import *


'''Files with functionality to call the py2 cli commandline functions from python3. This hack makes us able to 'call' python2 code from python3.'''

def _to_internal_request(reservation_request):
    allocrequest = _AllocRequest()
    for x in reservation_request.nodes:
        allocrequest.add(x.name, x.hw_type, x.image)
    return allocrequest


def _to_reservation_request(internalrequest):
    pass


def _get_py2_cli():
    import pathlib
    return fs.join(str(pathlib.Path(__file__).parent.absolute()), 'py2', 'cli.py')


def _py2_allocate(expiration, allocrequest, slicename, location, python='python'):
    cmd ='{} {} allocate {}'.format(python, _get_py2_cli(), expiration)
    if slicename != None:
        cmd += ' --name {}'.format(slicename)
    if location != None:
        cmd += ' --location {}'.format(location)
    with tempfile.TemporaryDirectory() as tmpdirname: # We use a tempfile to store the returned connectioninfo.
        path = fs.join(tmpdirname, 'metareserve_geni.tmp')
        cmd += ' --tmpoutloc {}'.format(path)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        process.communicate(str(allocrequest).encode('utf-8'))
        if process.returncode != 0:
            return None
        with open(path, 'r') as f:
            raw_infos = (_RawConnectInfo.from_string(line) for line in f.readlines())
    return [metareserve.reservation.Node(idx, node_name=x.name, ip_local=x.ip_local, ip_public=x.ip_public, port=x.port, extra_info={'username': x.user}) for idx, x in enumerate(raw_infos)]



def list_slices(slicename=None, location=None, show_all=False):
    '''List all slices, optionally with more detailed information.
    Args:
        slicename (optional str): If set, specifically searches for extra info for given slicename. Note: It is required to fill in a valid `location` argument if set.
        location (optional str): Must be set only when we need to search for a specific `slicename`.
        show_all (optional bool): If set, shows all entries. Otherwise, tries to filter out slicenames that are already expired.

    Returns:
        `True` on success, `False` otherwise.'''
    cmd = 'python {} list'.format(_get_py2_cli())
    if slicename != None:
        cmd += ' --name {}'.format(slicename)
    if location != None:
        cmd += ' --location {}'.format(location)
    if show_all:
        cmd += ' --all'
    return os.system(cmd) == 0


def deallocate(slicename, location):
    '''Deallocates slivers for a slice.
    Args:
        slicename: Name of the slice to deallocate slivers for.

    Returns:
        `True` on success, `False` otherwise.'''
    cmd = 'python {} deallocate'.format(_get_py2_cli())
    if slicename != None:
        cmd += ' --name {}'.format(slicename)
    if location != None:
        cmd += ' --location {}'.format(location)
    return os.system(cmd) == 0


def allocate(expiration, reservation_request):
    '''Allocates nodes for a cluster.
    Args:
        expiration (int): Slice expiration time in minutes. Also used as sliver deallocation time.
        reservation_request (GENIReservationRequest): Request object for allocation.

    Returns:
        List of `metareserve.reservation.Node` on success, `None` otherwise.'''
    allocrequest = _to_internal_request(reservation_request)
    val = _py2_allocate(expiration, allocrequest, reservation_request.slicename, reservation_request.location)
    if val:
        return val
    # Perhaps python2 executable is 'python2'
    return _py2_allocate(expiration, allocrequest, reservation_request.slicename, reservation_request.location, python='python2')