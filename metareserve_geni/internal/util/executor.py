import subprocess
import os
import threading
from internal.util.lock import Synchronized
# Synchronized
class Executor(object):
    '''Object to run subprocess commands in a separate thread.
    This way, Python can continue operating while interacting 
    with subprocesses.'''
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        self.started = False
        self.stopped = False
        self.thread = None
        self.process = None
        self.kwargs = kwargs

    def run(self):
        # Run our command. Returns immediately after booting a thread
        if self.started:
            raise RuntimeError('Executor already started. Make a new Executor for a new run')
        if self.stopped:
            raise RuntimeError('Executor already stopped. Make a new Executor for a new run')
        if self.kwargs == None:
            self.kwargs = kwargs

        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, **kwargs)
            self.process.communicate()
            self.stopped = True

        self.thread = threading.Thread(target=target, kwargs=self.kwargs)
        self.thread.start()
        self.started = True

    def run_direct(self):
        # Run our command on this thread, waiting until it completes.
        # Note: Some commands never return, be careful with this method!
        self.process = subprocess.Popen(self.cmd, **self.kwargs)
        self.started = True
        self.process.communicate()
        self.stopped = True
        return self.process.returncode

    def wait(self):
        '''Block until this executor is done.'''
        if not self.started:
            raise RuntimeError('Executor with command "{}" not yet started, cannot wait'.format(self.cmd))
        if self.stopped:
            return self.process.returncode
        self.thread.join()
        return self.process.returncode


    def stop(self):
        '''Force-stop executor, wait until done'''
        if self.started and not self.stopped:
            if self.thread.is_alive():
                #If command fails, or when stopping directly after starting
                for x in range(5):
                    if self.process == None:
                        time.sleep(1)
                    else:
                        break
                if self.process != None:
                    self.process.terminate()
                self.thread.join()
                self.stopped = True
        return self.process.returncode if self.process != None else 1


    def reboot(self):
        '''Stop and then start wrapped command again.'''
        self.stop()
        self.started = False
        self.stopped = False
        self.run(**self.kwargs)


    def get_pid(self):
        '''Returns pid of running process, or -1 if it cannot access current process.'''
        return -1 if (not self.started) or self.stopped or self.process == None else self.process.pid


    @staticmethod
    def run_all(executors):
        '''Function to run all given executors, with same arguments.'''
        for x in executors:
            x.run()

    @staticmethod
    def __print_errors(returncodes, executors):
        if any(x!=0 for x in returncodes):
            print('Experienced errors:')
            for idx, x in enumerate(returncodes):
                if x != 0:
                    print('\treturncode: {} - command: {}'.format(x, executors[idx].cmd))

    @staticmethod
    def wait_all(executors, stop_on_error=True, return_returncodes=False, print_on_error=False):
        '''Waits for all executors before returning control.
        Args:
            stop_on_error: If set, immediately kills all remaining executors when encountering an error. Otherwise, we continue executing the other executors.
            return_returncodes: If set, returns the process returncodes. Otherwise, returns regular `True`/`False` (see below).
            print_on_error: If set, prints the command(s) responsible for errors. Otherwise, this function is silent.
        
        Returns:
            `True` if all processes sucessfully executed, `False` otherwise.'''
        returncodes = []
        status = True
        for x in executors:
            returncode = x.wait()
            returncodes.append(returncode)
            if returncode != 0:
                if stop_on_error: # We had an error during execution and must stop all now
                    Executor.stop_all(executors) # Stop all other executors
                    if print_on_error:
                        Executor.__print_errors(returncodes, executors)
                    return returncodes if return_returncodes else False
                else:
                    status = False
        if print_on_error and not status:
            Executor.__print_errors(returncodes, executors)
            
        return returncodes if return_returncodes else status

    @staticmethod
    def stop_all(executors, as_generator=False):
        '''Function to stop all given execuors.
        Args:
            executors: Iterable of `Executor` to stop.
            as_generator: If set, returns exit status codes as a generator. Otherwise, does not return anything.

        Returns:
            nothing by default. If `as_generator` is  set, returns the exit status code for each executor.'''
        for x in executors:
            if as_generator:
                yield x.stop()
            else:
                x.stop()
