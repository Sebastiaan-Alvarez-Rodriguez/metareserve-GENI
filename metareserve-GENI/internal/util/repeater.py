import threading

class Repeater(threading.Thread):
    '''Simple object to repeat actions on a separate thread, every period seconds'''
    def __init__(self, func, period):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.func = func
        self.period = period

    # Executed by the parent, do not call this yourself.
    # To start the repeater, use r.start()
    def run(self):
        while not self.event.is_set():
            self.func()
            self.event.wait(self.period)

    # Stops the repeater
    def stop(self):
        self.event.set()