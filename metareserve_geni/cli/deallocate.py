import internal.gni.py2bridge as py2bridge
from internal.util.printer import *

'''CLI module to deallocate a cluster.'''



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
    if py2bridge.deallocate(args.name, args.location):
        prints('Resource deallocation success')
        return True
    return False
