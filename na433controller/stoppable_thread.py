#!/usr/bin/env python3

import threading

_flag_stop = threading.Event()

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kvargs):

        threading.Thread.__init__(self, *args, **kvargs)

    @property
    def stop(self):
        return _flag_stop.is_set()

    @stop.setter
    def stop(self, v):
        if v:
            _flag_stop.set()
