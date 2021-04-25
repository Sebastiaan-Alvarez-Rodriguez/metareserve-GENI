import datetime
from enum import Enum
import pprint
import sys
import time
from xmlrpclib import Fault
import geni.aggregate.cloudlab as cloudlab
import geni.aggregate.context
import geni.aggregate.pgutil
import geni.aggregate.protogeni
import geni.aggregate.frameworks
import geni.aggregate.apis
import geni.rspec.pg

from manifest.manifest import Manifest
from location.location import location_str
import sharedutil

'''File containing generic functions for resource operations (create, renew, delete, list).'''


class CreationState(Enum):
    '''Trivial enum representation of possible creation calls in GENI in general.'''
    FAILED = 0 # Did not create anything.
    CREATED = 1 # Created object.
    EXISTS = 2 # Did not create anything, object already exists.
    RENEWED = 3 # Object exists, renewed expiration.


def slice_list(ctx, corrected=True):
    '''List available slices for this project. Also tries to fix inherently broken GENI by filtering wrong entries.'''
    now = datetime.datetime.now()
    for x in ctx.cf.listSlices(ctx).keys():
        if (not corrected) or (not 'metareserve' in x) or ctx.getSliceInfo(x.split('+')[-1]).expires > now:
            yield x

def print_slicelist(ctx, slicename=None, corrected=True):
    '''Prints the list of currently available slices. Uses colors for visual grepping. 
    Cyan entries are reservations created by this tool. Purple entries are the ones we are looking for at the moment.
    Sorts our slicenames (the ones with "metareserve" in them) to the front.

    Args:
        ctx: geni-lib context.
        slicename (str): Slicename we are looking for. If set, we use purple coloring to indicate name matches.'''
    PRP = '\033[1;35m'
    CAN = '\033[1;36m'
    CLR = '\033[0m'
    print('Available slices{}:'.format(' (corrected)' if corrected else ''))
    names = list(slice_list(ctx, corrected=corrected))
    for x in (y for y in names if 'metareserve' in y):
        startcolor = PRP if slicename != None and slicename == x.split('+')[-1] else CAN 
        print('\t{}{}{}'.format(startcolor, x, CLR))
    for x in (y for y in names if not 'metareserve' in y):
        print('\t{}'.format(x))


def slice_renew(ctx, slicename, expiration=60*24*7, retries=5, retries_sleep=5):
    '''Renews a slice.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        (`CreationState`, `datetime`): Arg 1 indicates what happened in this function. Arg 2 is a datetime if arg 1 == RENEWED. Otherwise, it returns the human-understandable error cause.
    '''
    if not sharedutil.lowercase_alpha(slicename):
        print('Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))
        return False
    
    date = sharedutil.datetime_get(expiration)
    for x in range(retries): 
        try:
            something = ctx.cf.renewSlice(ctx, slicename, exp=date)
            # We get an empty dict in the `something` variable.
            return (CreationState.RENEWED, date)
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
        except geni.aggregate.context.SliceCredInfo.CredentialExpiredError as e:
            e_msg = str(e).strip().replace('\n', ' ')
            if 'expired on' in e_msg:
                return (CreationState.FAILED, 'Remote still has an expired slicename with the same name ("{}") in memory. (Determined from error msg: {}). Please pick another slicename.'.format(slicename, e))
    return (CreationState.FAILED, 'Experienced error: 503: Server temporarily offline')


def slice_create(ctx, slicename, expiration=60*24*7, renew_exist=True, retries=5, retries_sleep=5):
    '''Creates (or optionally renews) a slice.
    Because GENI is inherently broken, we cannot trust any listings about existing slices it gives.
    They can have expired already.
    Instead, we just try to create the slice, and if that fails, then we know it exists and renew it.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.
        renew_exist (bool): If set, renews the slice, setting the expiration date at `expiration` minutes from now.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        (`CreationState`, `datetime`): Arg 1 indicates what happened in this function. Arg 2 is a datetime if arg 1 == CREATED | EXISTS | RENEWED
    '''
    if not sharedutil.lowercase_alpha(slicename):
        return (CreationState.FAILED, 'Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))

    for x in range(retries): 
        try:
            slice_id = ('urn:publicid:IDN+emulab.net:{}+slice+{}').format(ctx.project, slicename)
            date = sharedutil.datetime_get(expiration)
            print_slicelist(ctx, slicename)
            print('Creating slice {}, date set to {}.'.format(slice_id, date))
            ctx.cf.createSlice(ctx, slicename, exp=date)
            return (CreationState.CREATED, date)
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
        except geni.aggregate.frameworks.ClearinghouseError as e:
            if 'already a registered slice' in str(e):
                if renew_exist:
                    print('Renewing slice, set expiration date to {}.'.format(date))
                    return slice_renew(ctx, slicename, date, retries, retries_sleep)
                else:
                    date = ctx.getSliceInfo(slicename).expires
                    print('Skipping renewing slice. Expiration date remains {}'.format(date))
                    return (CreationState.EXISTS, date) 
            if x != retries-1:
                time.sleep(retries_sleep)
    return (CreationState.FAILED, 'Experienced error: 503: Server temporarily offline')



def sliver_create(ctx, slicename, request, location=geni.aggregate.protogeni.UTAH_PG, expiration=60*24*7, renew_exist=True, retries=5, retries_sleep=5, wait_ready=True, wait_sleep=15, wait_stop=60*10):
    '''Creates (or optionally renews) a sliver on selected site. Requires an existing slice with given `slicename`.

    Args:
        ctx: geni-lib context
        slicename (str): Slice name.
        request: GENI `Request` object with machines to allocate.
        location: physical cluster site. Picked site must support spawning images on raw hardware.
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.
        renew_exist (bool): If set, renews the slice, setting the expiration date at `expiration` minutes from now.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.
        wait_ready (bool): If set, this function will block until the VM is ready.
        wait_sleep: Number of seconds to wait between ready-checks.
        wait_stop: Number of seconds before we give up on waiting for a ready-status. Stopping before being ready counts as a failure.

    Returns:
        A `Manifest` on success, `None` on failure.
    '''
    # TODO: how to set expiration time when creating? Is the current default equal to the lifetime of the slice?
    for x in range(retries):
        try:
            print('Creating sliver...')
            manifest = location.createsliver(ctx, slicename, request)
            if wait_ready:
                print('Sliver creation request sent. Waiting for ready-state...')
                if not sliver_wait(ctx, slicename, location=location, wait_sleep=wait_sleep, wait_stop=wait_stop):
                    print('[ERROR] Did not receive sliver ready status within allocated time.')
                    return None
            print('Done!')
            return Manifest(manifest)
        except geni.aggregate.pgutil.NoMappingError as e:
            print('Problems detected with mapping. Does the aggregate support what you are doing? (spawning VMs/images on raw hardware?)')
            print(e)
            return None
        except geni.aggregate.pgutil.ProtoGENIError as e:
            e_msg = str(e).strip().replace('\n', ' ')
            if 'Resource reservation violation' in e_msg:
                print('Found resource reservation violation response (are there enough nodes free at the moment?):\n{}'.format(e))
                return None
            print('Sliver already exists (determined from error msg: {})'.format(e))
            if renew_exist:
                if not sliver_renew(ctx, slicename, location, expiration, retries-x, retries_sleep):
                    return None # Failed to renew sliver
            return sliver_res(ctx, slicename, location, retries-x, retries_sleep)
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
    return None


def sliver_renew(ctx, slicename, location=geni.aggregate.protogeni.UTAH_PG, expiration=60*24*7, retries=5, retries_sleep=5):
    '''Renews a sliver. Used to set the expiration date of a sliver at a later point in time.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        location: physical cluster site.
        expiration: If `int` type, used as slice expiration time in minutes from now. If `datetime` type, used as the expiration date.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        `True on success`, `False` on failure.
    '''
    if not sharedutil.lowercase_alpha(slicename):
        print('Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))
        return False

    for x in range(retries):
        try:
            date = sharedutil.datetime_get(expiration)
            print('Renewing sliver, set expiration date to {}'.format(date))
            success = location.renewsliver(ctx, slicename, date)
            return success
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
    return False


def sliver_res(ctx, slicename, location=geni.aggregate.protogeni.UTAH_PG, retries=5, retries_sleep=5):
    '''Returns the resources allocated to a sliver.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        location: physical cluster site.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        A Manifest on success, `None` on failure.
    '''
    if not sharedutil.lowercase_alpha(slicename):
        print('Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))
        return None

    for x in range(retries):
        try:
            manifest = location.listresources(ctx, sname=slicename)
            return Manifest(manifest)
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
        except geni.aggregate.frameworks.ClearinghouseError as e:
            if isinstance(e, geni.aggregate.frameworks.ClearinghouseError) and 'No such Slice' in str(e):
                print('Cannot fetch state for slice named "{}", as it does not exist.'.format(slicename))
                return None
            if x != retries-1:
                time.sleep(retries_sleep)
        except geni.aggregate.pgutil.ProtoGENIError as e:
            if 'Nothing here by that name' in str(e):
                print('Cannot find given (known) slice "{}" on location "{}".'.format(slicename, location_str(location)))
                return None
            else:
                print e
    return None


def sliver_status(ctx, slicename, location=geni.aggregate.protogeni.UTAH_PG, retries=5, retries_sleep=5):
    '''Returns sliver status. Primarily useful to check whether a reserved resource has become active.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        location: physical cluster site.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        A status dictionary (much like a raw manifest) on success, `None` on failure. 
    '''
    for x in range(retries):
        try:
            return location.sliverstatus(ctx, slicename)
        except Exception as e:
            time.sleep(retries_sleep)
    return None


def sliver_wait(ctx, slicename, location=geni.aggregate.protogeni.UTAH_PG, retries=5, retries_sleep=5, wait_sleep=15, wait_stop=60*10):
    '''Blocks until sliver is ready.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        location: physical cluster site.
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.
        wait_sleep: Number of seconds to wait between ready-checks.
        wait_stop: Number of seconds before we stop trying.

    Returns:
        `True` if the sliver is ready. `False` if we reached the `wait_stop` timepoint before we received a ready-status.
    '''
    endtime = time.time() + wait_stop
    while True:
        status = sliver_status(ctx, slicename, location, retries, retries_sleep)
        if status and status['pg_status'] == 'ready':
            return True
        if time.time() > endtime:
            return False
        else:
            time.sleep(wait_sleep)


def sliver_deallocate(ctx, slicename, location=geni.aggregate.protogeni.UTAH_PG, retries=5, retries_sleep=5):
    '''Deallocates a sliver.

    Args:
        ctx: geni-lib context.
        slicename (str): Slice name.
        location: physical cluster site
        retries: Number of retries when we get a "503: Server temporarily offline" before we stop trying.
        retries_sleep: Number of seconds to sleep for each retry.

    Returns:
        `True` on success, `False` on failure.
    '''
    if not sharedutil.lowercase_alpha(slicename):
        print('Slicename must be all lowercase alphabetic characters, found: {}'.format(slicename))
        return False

    for x in range(retries):
        try:
            location.deletesliver(ctx, slicename)
            return True
        except Fault as e:
            if x != retries-1:
                time.sleep(retries_sleep)
        except geni.aggregate.apis.DeleteSliverError as e:
            if 'No such slice here' in str(e):
                print('Cannot find given (known) slice "{}" on location "{}". Perhaps it no longer exists?'.format(slicename, location_str(location)))
                return None
            else:
                raise e
        except geni.aggregate.context.SliceCredInfo.CredentialExpiredError as e:
            print(e) # Our 'credential expired', meaning the slice no longer exists.
            return None
    return False