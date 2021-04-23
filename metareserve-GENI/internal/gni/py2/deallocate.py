import allocate.cph as ceph
from allocrequest import AllocRequest
import location.location as locutil

'''CLI module to deallocate a cluster.'''

def get_context():
    return geni.util.loadContext()


def deallocate(slicename, location):
    return generic.sliver_deallocate(get_context(), slicename, location=locutil.location_get(location))


def subparser(subparsers):
    '''Register subparser modules'''
    deallocateparser = subparsers.add_parser('deallocate', help='deallocate cluster on U.S. federal government clusters.')
    deallocateparser.add_argument('-n', '--name', metavar='name', default='metareserve', help='Name for slice on US resource (default="metareserve")')
    deallocateparser.add_argument('-l', '--location', metavar='location', nargs='?', default='cl-utah', const='cl-utah', help='Location of allocation (default="cl-utah", which is CloudLab, Utah site)')
    
    return [deallocateparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'deallocate'


def deploy(parsers, args):
    return deallocate_ceph(args.name, args.location)
