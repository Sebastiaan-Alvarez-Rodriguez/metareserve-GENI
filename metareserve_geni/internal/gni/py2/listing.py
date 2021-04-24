import geni.util

import alloc.generic as generic
import location.location as locutil


'''CLI module to list GENI reources.'''

def get_context():
    return geni.util.loadContext()


def list_slices(slicename=None, location=None, corrected=True):
    if (slicename and not location) or location and not slicename:
        print('[ERROR] When specifying slicename, must specify location and viceversa.')
        return False
    ctx = get_context()
    generic.print_slicelist(ctx, slicename=slicename, corrected=corrected)
    if slicename != None:
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
                print('Could not display slice info.')
                return False
            print('number of nodes: {}'.format(manifest.num_nodes))
            print('Connection infos:')
            for x in sorted(manifest.get_connect_info(), key=lambda x: x.name):
                print('\t{}'.format(x))
    return True


def subparser(subparsers):
    '''Register subparser modules'''
    listsliceparser = subparsers.add_parser('list', help='List cluster info for U.S. federal government clusters.')
    listsliceparser.add_argument('-n', '--name', metavar='name', nargs='?', default=None, const='msparkceph', help='Name of slice on US resource (if no arg, default="msparkceph")')
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
    return list_slices(args.name, args.location, not args.all)
