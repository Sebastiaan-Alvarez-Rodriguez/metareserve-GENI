from functools import wraps
from threading import Lock

# File which provides Java-style class locking

def synchronized(lock):
    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)
        return inner_wrapper
    return wrapper


class Synchronized:
    # Make object-level lock (no 2 functions of object may run concurrently)
    # Usage:
    #     class <name>(Synchronized):...
    def __init_subclass__(cls, **kw):
        synchronizer = synchronized(Lock())
        for name in cls.__dict__:
            attr = getattr(cls, name)
            if callable(attr):
                setattr(cls, name, synchronized(attr))