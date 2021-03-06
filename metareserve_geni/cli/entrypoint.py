import argparse

import os
import sys

'''Python CLI module to make geni allocations.'''


sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))) # Appends main project root as importpath.


def _get_modules():
    import cli.allocate as allocate
    import cli.deallocate as deallocate
    import cli.listing as listing
    return [allocate, deallocate, listing]


# Register subparser modules
def subparser(parser):
    subparsers = parser.add_subparsers(help='Subcommands', dest='command')
    return [x.subparser(subparsers) for x in _get_modules()]


# Processing of deploy commandline args occurs here
def deploy(mainparser, parsers, args):
    for parsers_for_module, module in zip(parsers, _get_modules()):
        if module.deploy_args_set(args):
            return module.deploy(parsers_for_module, args)
    mainparser.print_help()
    return True


def main():
    parser = argparse.ArgumentParser(
        prog='geni-reserve',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Simple GENI reservations'
    )
    retval = True
    geniparsers = subparser(parser)

    args = parser.parse_args()
    retval = deploy(parser, geniparsers, args)

    if isinstance(retval, bool):
        exit(0 if retval else 1)
    elif isinstance(retval, int):
        exit(retval)
    else:
        exit(0 if retval else 1)


if __name__ == '__main__':
    main()