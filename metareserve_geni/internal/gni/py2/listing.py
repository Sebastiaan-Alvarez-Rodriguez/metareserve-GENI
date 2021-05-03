import argparse
import datetime

import alloc.generic as generic
import location.location as locutil
import util.geni_util as geni_util


'''CLI module to list GENI reources.'''


def list_slices(slicename=None, location=None, corrected=True, tmpoutloc=None):
    '''List all slices. If both `slicename` and `location` are set, prints detailed info for that particular slice.
    Args:
        slicename (optional str): If set, we print specific info for that slice. Requires `location` to be set`.
        location (optional str): Location of given `slicename`. Must be set alonside `slicename` argument.
        corrected (optional bool): If set, corrects list of displayed slices by removing expired entries. Leaves as-is otherwise.
        tmpoutloc (optional str): If set, writes `RawConnectInfo` in given loc.

    Returns:
        `True` on success, `False` otherwise.'''
    if (slicename and not location) or location and not slicename:
        print('[ERROR] When specifying slicename, must specify location and viceversa.')
        return False
    ctx = geni_util.get_context()
    if not ctx:
        return False
    generic.print_slicelist(ctx, slicename=slicename, corrected=corrected)
    if slicename:
        print('')
        print('Fetching specific info for slice "{}"...'.format(slicename))
        info = ctx.getSliceInfo(slicename)
        print('path: {}'.format(info._path))
        print('expiration: {}'.format(info.expires))
        did_expire = info.expires <= datetime.datetime.now()
        if did_expire: # Slice expired
            print('\tNote: This slice has expired.')
        print('urn: {}'.format(info.urn))
        print('type: {}'.format(info.type))
        print('version: {}'.format(info.version))
        
        if not did_expire:
            manifest = generic.sliver_res(ctx, slicename, location=locutil.location_get(location))
            if not manifest:
                print('Has this slice recently been deleted?')
                print('Could not display slice info.')
                return False
            print('number of nodes: {}'.format(manifest.num_nodes))
            infos = sorted(manifest.get_connect_info(), key=lambda x: x.name)
            with open(tmpoutloc, 'w') as f:
                f.write('\n'.join(str(x) for x in infos))
    return True


def subparser(subparsers):
    '''Register subparser modules'''
    listsliceparser = subparsers.add_parser('list', help='List cluster info for U.S. federal government clusters.')
    listsliceparser.add_argument('-n', '--name', metavar='name', nargs='?', default=None, const='metareserve', help='Name of slice on US resource (if no arg, default="metareserve")')
    listsliceparser.add_argument('-l', '--location', metavar='location', nargs='?', default=None, const='cl-utah', help='Name of slice on US resource (if no arg, default="cl-utah", which is CloudLab, Utah site)')
    listsliceparser.add_argument('-a', '--all', help='Print all slice given by GENI, even wrong entries (we filter away known expired entries by default).', action='store_true')
    listsliceparser.add_argument('--tmpoutloc', nargs='?', default=None, const=None, help=argparse.SUPPRESS)
    return [listsliceparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'list'


def deploy(parsers, args):
    return list_slices(args.name, args.location, not args.all, args.tmpoutloc)
