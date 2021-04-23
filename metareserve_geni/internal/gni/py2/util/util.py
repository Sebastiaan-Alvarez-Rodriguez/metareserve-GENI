import datetime
import sys
import subprocess


def get_version(packagename):
    '''Checks the version of an installed package.

    Args:
        packagename: Name of package.

    Returns:
        Version string for package on success, `None` on failure.
    '''
    try:
        if sys.version_info >= (3, 8):
            from importlib.metadata import version
            return version(packagename)
        else:
            res = subprocess.check_output('pip freeze | grep {} | awk -F\'=\' \'{print $NF}\''.format(packagename)).decode('UTF-8').strip()
            if len(res) == 0:
                return None
            return res
    except Exception as e:
        return None



def ensure_version(nums, string, greater_allowed=True):
    '''Returns `True` if given version array (e.g. [0,9,9,2] for '0.9.9.2') is equal to given version string.
    By default, `greater_allowed==True`, which allows version strings with a higher version to be accepted.
    
    Args:
        nums (array of ints): Ordered version number sequence.
        string (string): Version string to check.
        greater_allowed (bool): Toggles whether we allow version strings greater than represented by `nums`. If false, we require an exact match.
    Returns:
        `True` if `string` matches version indicated by `nums` (or is greater, optional), `False` otherwise.
    '''
    if not string: # when passed `None` as version string, we assume that means there is no version.
        return False
    for idx, x in enumerate(nums):
        try:
            found, string = string.split('.', 1)
        except ValueError as e: # Previous version numbers equal to minimum, now out of numbers
            return not any(x for x in nums[idx:] if x > 0) # Return True if minimum has only zeroes from here
        
        if int(found) > x: # Current version number larger than minimum required
            return True and greater_allowed
        elif int(found) < x: # Previous version numbers equal to minimum, now smaller
            return False