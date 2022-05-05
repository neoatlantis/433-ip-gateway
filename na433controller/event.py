#!/usr/bin/env python3

class EventEmitter(list):

    def __init__(self):
        list.__init__(self)

    def __call__(self, *args, **kvargs):
        for func in self:
            func(*args, **kvargs)
