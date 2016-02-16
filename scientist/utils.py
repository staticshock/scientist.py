import time


class Timer(object):
    def __init__(self, start=True):
        if start:
            self.start()

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.stop_time = time.time()
        return self.duration

    @property
    def duration(self):
        return self.stop_time - self.start_time
