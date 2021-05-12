# This file contains many functions to help interact 
# with the filesystem in an OS independent manner
# 
# This mainly is a wrapper around the system's os libraries.
# Quite a few handy tricks are stored here.

import os
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile, ZipInfo


def abspath(path=os.path.dirname(sys.argv[0])):
    return os.path.abspath(path)

# Returns absolute path for a given file
def abspathfile(file):
    return os.path.abspath(os.path.dirname(file))

def basename(path):
    return os.path.basename(path)

def cp(path_src, path_dst):
    if isfile(path_src):
        shutil.copy2(path_src, path_dst)
    else:
        shutil.copytree(path_src, path_dst)

def cwd():
    return os.getcwd()

def dirname(path):
    return os.path.dirname(path)

def exists(path, *args):
    return os.path.exists(join(path,*args))

def isdir(path, *args):
    return os.path.isdir(join(path,*args))

def isemptydir(path, *args):
    try:
        next(ls(path, *args))
        return False
    except StopIteration as e:
        return True

def isfile(path, *args):
    return os.path.isfile(join(path,*args))

# Note: Returns always False on unsupported systems.
# Note: Be careful: Even if given symlink points to non-existing target, returns True
def issymlink(path, *args):
    return os.path.islink(join(path, *args))

# Resolve a symlink. With full_resolve, 
# we keep following links until we find end destination
def resolvelink(path, *args, full_resolve=True):
    return str(Path(join(path, *args)).resolve().absolute()) if full_resolve else os.readlink(join(path, *args))

def join(directory, *args):
    returnstring = directory
    for arg in args:
        returnstring = os.path.join(returnstring, str(arg))
    return returnstring

def ln(pointedloc, pointerloc, soft=True, is_dir=None):
    if soft: # Make softlink
        os.symlink(pointedloc, pointerloc, target_is_directory=isdir(pointedloc) if is_dir == None else is_dir)
    else: # Make hardlink
        os.link(pointedloc, pointerloc)

def ls(directory, only_files=False, only_dirs=False, full_paths=False, *args):
    ddir = join(directory, *args)
    if only_files and only_dirs:
        raise ValueError('Cannot ls only files and only directories')

    if sys.version_info >= (3, 5): # Use faster implementation in python 3.5 and above
        with os.scandir(ddir) as it:
            for entry in it:
                if (entry.is_dir() and not only_files) or (entry.is_file() and not only_dirs):
                    yield join(ddir, entry.name) if full_paths else entry.name
    else: # Use significantly slower implementation available in python 3.4 and below
        for entry in os.listdir(ddir):
            if (isdir(ddir, entry) and not only_files) or (isfile(ddir, entry) and not only_dirs):
                yield join(ddir, entry) if full_paths else entry

def mkdir(path, *args, exist_ok=False):
    os.makedirs(join(path, *args), exist_ok=exist_ok)

def mv(path_src, path_dst):
    shutil.move(path_src, path_dst)

def rm(directory, *args, ignore_errors=False):
    path = join(directory, *args)
    if isdir(path):
        shutil.rmtree(path, ignore_errors=ignore_errors)
    else:
        if ignore_errors:
            try:
                os.remove(path)
            except Exception as e:
                pass
        else:
            os.remove(path)


def sep():
    return os.sep

# Return size of file in bytes
def sizeof(directory, *args):
    path = join(directory, *args)
    if not isfile(path):
        raise RuntimeError('Error: "{}" is no path to a file'.format(path))
    return os.path.getsize(path)

def split(path):
    return path.split(os.sep)

# Touch-like command, does not emulate mtime if file already exists
def touch(path, *args):
    path = join(path, *args)
    if exists(path):
        raise RuntimeError('Error: "{}" already exists'.format(path))
    open(path, 'w').close()


def unpack(filename, extract_dir):
    if not filename.endswith('.zip'):
        shutil.unpack_archive(filename, extract_dir)
    # Below code is taken from the shutil implementation: https://github.com/python/cpython/blob/78b2abca8e96b43f56ab1b9ad673aaa6bbe7e790/Lib/shutil.py#L1152-L1181
    # All credits for this code to them. We changed it to work with our zipfile object, which maintains file permissions. Also, we substituted a function to make directories with our own.
    import zipfile  # late import for breaking circular dependency
    if not zipfile.is_zipfile(filename):
        raise ReadError("%s is not a zip file" % filename)
    zip = _ZipFileWithpermissions(filename)
    try:
        for info in zip.infolist():
            name = info.filename
            # don't extract absolute paths or ones with .. in them
            if name.startswith('/') or '..' in name:
                continue
            target = join(extract_dir, *name.split('/'))
            if not target:
                continue
            mkdir(dirname(target), exist_ok=True)
            if not name.endswith('/'):
                # file
                data = zip.read(info.filename)
                f = open(target, 'wb')
                try:
                    f.write(data)
                finally:
                    f.close()
                    del data
                attr = info.external_attr >> 16
                if attr != 0:
                    os.chmod(target, attr)
    finally:
        zip.close()


class _ZipFileWithpermissions(ZipFile):
    '''Zipfile implementation that fixes https://bugs.python.org/issue15795. No one knows why this fix is not merged into the ZipFile project.'''
    if sys.version_info <= (3, 5):
        def extract(self, member, path=None, pwd=None):
            if not isinstance(member, ZipInfo):
                member = self.getinfo(member)

            if path is None:
                path = os.getcwd()

            ret_val = self._extract_member(member, path, pwd)
            attr = member.external_attr >> 16
            os.chmod(ret_val, attr)
            return ret_val
    else:
        def _extract_member(self, member, targetpath, pwd):
            if not isinstance(member, ZipInfo):
                member = self.getinfo(member)

            targetpath = super()._extract_member(member, targetpath, pwd)

            attr = member.external_attr >> 16
            if attr != 0:
                os.chmod(targetpath, attr)
            return targetpath
