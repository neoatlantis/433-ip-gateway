#!/usr/bin/env python3

import os
import sys
import time
import threading
import queue
import re
import json
import serial

from .serial_commander import ArduinoStateTracker, SerialCommander




class DeviceController:

    def __init__(self):
        self.serial_state_tracker = ArduinoStateTracker()
        self.flag_exit = threading.Event()
        self._t = None

        def p(i):
            print(i)
        self.serial_state_tracker.append(p)

    def loop(self):
        while not self.flag_exit.is_set():
            if None != self._t:
                print("Serial communication broken. Restart...")
            self._t = threading.Thread(target=self._listen_job)
            self._t.start()
            while not self.flag_exit.is_set():
                try:
                    if self._t.is_alive(): time.sleep(1)
                except KeyboardInterrupt as e:
                    self.flag_exit.set()


    def __enter__(self, *args, **kvargs):
        return self

    def __exit__(self, *args, **kvargs):
        self.flag_exit.set()

    def _listen_job(self):
        with SerialCommander(
            port=sys.argv[1],
            baudrate=9600,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=None
        ) as s:
            while not s.flag_exit.is_set():
                try:
                    r = s.read_queue.get(timeout=1)
                    self.serial_state_tracker.feed(r)
                except KeyboardInterrupt as e:
                    exit()
                except Exception:
                    pass


if __name__ == "__main__":
    with DeviceController() as dc:
        dc.loop()
