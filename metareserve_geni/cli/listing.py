import internal.gni.py2bridge as py2bridge
from internal.util.printer import *

'''CLI module to list GENI reources.'''


def subparser(subparsers):
    '''Register subparser modules'''
    listsliceparser = subparsers.add_parser('list', help='List cluster info for U.S. federal government clusters.')
    listsliceparser.add_argument('-n', '--name', metavar='name', nargs='?', default=None, const='metareserve', help='Name of slice on US resource (if no arg, default="metareserve")')
    listsliceparser.add_argument('-l', '--location', metavar='location', nargs='?', default=None, const='cl-utah', help='Name of slice on US resource (if no arg, default="cl-utah", which is CloudLab, Utah site)')
    listsliceparser.add_argument('-a', '--all', help='Print all slice given by GENI, even wrong entries (we filter away known expired entries by default).', action='store_true')

    return [listsliceparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'list'


def deploy(parsers, args):
    return py2bridge.list_slices(slicename=args.name, location=args.location, show_all=args.all)