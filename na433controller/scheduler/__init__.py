#!/usr/bin/env python3

import time
import croniter
from ..stoppable_thread import StoppableThread


class Scheduler(StoppableThread):

    def __init__(self, schedule, device_controller):
        StoppableThread.__init__(self)

        self.__rules = schedule


    def run(self):
        while not self.stop:
            time.sleep(1)
            print("***")

    def __enter__(self, *args, **kvargs):
        self.start()
        return self

    def __exit__(self, *args, **kvargs):
        self.stop = True



def run_scheduler(schedule, device_controller):
    scheduler = Scheduler(
        schedule=schedule,
        device_controller=device_controller
    )
    exit()
    scheduler.start()
