import argparse

import os
import sys

import util.deps as deps

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0]))), 'shared'))

'''Python CLI for python2, so we can access GENI methods from python2. We need that, as GENI only works with python2.'''

def _get_modules():
    import allocate
    import deallocate
    import listing
    return [allocate, deallocate, listing]


# Register subparser modules
def subparser(parser):
    subparsers = parser.add_subparsers(help='Subcommands', dest='command')
    return [x.subparser(subparsers) for x in _get_modules()]


# Processing of deploy commandline args occurs here
def deploy(parsers, args):
    for parsers_for_module, module in zip(parsers, _get_modules()):
        if module.deploy_args_set(args):
            return module.deploy(parsers_for_module, args)
    deployparser.print_help()
    return True


def main():
    if not deps.geni_check(silent=False):
        print('There were unmet dependencies for python2. Please install the correct versions of missing packages in (!!!) python2 (!!!) and try again.')
        return False
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    retval = True
    geniparsers = subparser(parser)

    args = parser.parse_args()
    retval = deploy(geniparsers, args)

    if isinstance(retval, bool):
        exit(0 if retval else 1)
    else: #retval will be an int
        exit(retval)


if __name__ == '__main__':
    main()