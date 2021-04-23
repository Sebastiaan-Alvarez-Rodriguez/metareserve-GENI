import util as gutil


def geni_lib_check():
    try:
        import geni
        return True
    except Exception as e:
        return False

# GENI needs the `six` package installed, but does not specify this in manifest. Therefore, We check it ourselves.
# Returns `True` if `six` installed, `False` otherwise.
def geni_six_check():
    try:
        import six
        return True
    except Exception as e:
        return False


# GENI uses `lxml` package. `lxml` needs python>=3.5 or python==2.7.
def geni_lxml_check():
    try:
        import lxml
        return True
    except Exception as e:
        return False


# Checks all dependencies at once. Returns `True` when all dependencies are satisfied.
def geni_dependency_checks():
    for x in (geni_lib_check, geni_six_check, geni_lxml_check):
        if not x():
            return False
    return True


# Returns `True` if geni-lib==0.9.9.2 is installed, with all needed dependencies, `False` otherwise.
# Optionally turn off checking dependencies with the `check_deps` param.
def geni_check(check_deps=True):
    if (not check_deps) and not geni_dependency_checks():
        return False
    return gutil.ensure_version([0,9,9,2], gutil.get_version('geni-lib'), greater_allowed=False)