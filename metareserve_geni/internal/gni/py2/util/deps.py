import util as gutil


def geni_lib_check():
    try:
        import geni
        return True
    except Exception as e:
        if not silent:
            print('dependency not met: geni-lib')
        return False

# GENI needs the `six` package installed, but does not specify this in manifest. Therefore, We check it ourselves.
# Returns `True` if `six` installed, `False` otherwise.
def geni_six_check():
    try:
        import six
        return True
    except Exception as e:
        if not silent:
            print('dependency not met: six')
        return False


def geni_lxml_check(silent):
    # GENI uses `lxml` package. `lxml` needs python>=3.5 or python==2.7.
    try:
        import lxml
        return True
    except Exception as e:
        if not silent:
            print('dependency not met: lxml')
        return False


# Checks all dependencies at once. Returns `True` when all dependencies are satisfied.
def geni_dependency_checks(silent=False):
    status = True
    for x in (geni_lib_check, geni_six_check, geni_lxml_check):
        if not x(silent):
            status = False
    return status


def geni_check(check_deps=True, silent=False):
    '''Checks all dependencies for geni.
    Args:
        check_deps (optional bool): If set, we check not only geni-lib, but also the geni-lib requirements (lxml and six packages).
        silent (optional bool): If set, does not print useful user output.

    Returns:
        `True` when all dependencies met, `False` otherwise.'''

    if (not check_deps) and not geni_dependency_checks(silent):
        return False

    geni_required_version = [0,9,9,2]
    geni_found_version = gutil.get_version('geni-lib')
    if not gutil.ensure_version(geni_required_version, geni_found_version, greater_allowed=False):
        print('dependency "geni-lib" has incorrect version "{}", require version {}'.format(geni_found_version, '.'.join(str(x) for x in geni_required_version)))
        return False
    return True