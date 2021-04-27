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


def _get_py2_executable_name():
    '''Simple function trying to find the python2 executable name.
    Returns:
        The name of the python2 executable on success, `None` otherwise.'''
    if subprocess.call('which python2', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0:
        return 'python2'
    if subprocess.call('which python', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0:
        return 'python'
    return None


def _py2_exec_get_nodes(cmd, stdin=None):
    '''Executes py2bridge commands which expect to get `metareserve.Node` back.
    Args:
        cmd (str): Command to execute. Note: We append a '--tmpoutloc path/to/tmpdir' arg, where we store returning info.
        stdin (optional str): If set, given string will be sent to the stdin of the python2 application. Note: Encoding to utf-8 happens inside this function.

    Returns:
        List of `metareserve.Node` on success, `None` on failure.'''
    with tempfile.TemporaryDirectory() as tmpdirname: # We use a tempfile to store the returned connectioninfo.
        path = fs.join(tmpdirname, 'metareserve_geni.tmp')
        cmd += ' --tmpoutloc {}'.format(path)

        if stdin:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
            process.communicate(stdin.encode('utf-8'))
        else:
            process = subprocess.Popen(cmd, shell=True)
            process.communicate()
        if process.returncode != 0:
            return (False, None)
        with open(path, 'r') as f:
            try:
                raw_infos = (_RawConnectInfo.from_string(line) for line in f.readlines())
            except Exception as e: # Could not read info, but we had a 0 exit status code. Probably, slice referenced has expired.
                return (True, None)
    return (True, [metareserve.Node(idx, node_name=x.name, ip_local=x.ip_local, ip_public=x.ip_public, port=x.port, extra_info={'user': x.user}) for idx, x in enumerate(raw_infos)])


def list_slices(slicename=None, location=None, show_all=False):
    '''List all slices, optionally with more detailed information.
    Args:
        slicename (optional str): If set, specifically searches for extra info for given slicename. Note: It is required to fill in a valid `location` argument if set.
        location (optional str): Must be set only when we need to search for a specific `slicename`.
        show_all (optional bool): If set, shows all entries. Otherwise, tries to filter out slicenames that are already expired.

    Returns:
        `True` on success, `False` otherwise.'''
    cmd = '{} {} list'.format(_get_py2_executable_name(), _get_py2_cli())
    if slicename:
        cmd += ' --name {}'.format(slicename)
    if location:
        cmd += ' --location {}'.format(location)
    if show_all:
        cmd += ' --all'
    if slicename and location:
        success, nodes = _py2_exec_get_nodes(cmd)
        if not nodes:
            return success
        print('Reservation:')
        print('id,hostname,ip_local,ip_public,port,extra_info')
        print(metareserve.Reservation(nodes))
        return True
    return os.system(cmd) == 0


def deallocate(slicename, location):
    '''Deallocates slivers for a slice.
    Args:
        slicename: Name of the slice to deallocate slivers for.

    Returns:
        `True` on success, `False` otherwise.'''
    cmd = '{} {} deallocate'.format(_get_py2_executable_name(), _get_py2_cli())
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
    cmd ='{} {} allocate {}'.format(_get_py2_executable_name(), _get_py2_cli(), expiration)
    if slicename != None:
        cmd += ' --name {}'.format(reservation_request.slicename)
    if location != None:
        cmd += ' --location {}'.format(reservation_request.location)

    allocrequest = _to_internal_request(reservation_request)
    _, nodes = _py2_exec_get_nodes(cmd, stdin=str(allocrequest))
    return nodes
