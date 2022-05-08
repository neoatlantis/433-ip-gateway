#!/usr/bin/env python3

import os
import sys
import time
import threading
import queue
import re
import json
import serial

from .devices import PreconfiguredDevices
from .serial_commander import SerialCommander
from .stoppable_thread import StoppableThread


class DeviceController(StoppableThread):

    def __init__(self, devices_config, **kvargs):
        StoppableThread.__init__(self)
        
        self.__preconfigured_devices = PreconfiguredDevices(devices_config)
        self.__sc_kvargs = kvargs
        self.__send_queue = queue.Queue()

        self.state = None

    def __read_signal_buffer(self):
        if self.state and "signal_buffer" in self.state:
            return self.state["signal_buffer"]
        return None

    def __read_signal_sent(self):
        if self.state and "signal_sent" in self.state:
            return self.state["signal_sent"]
        return None

    def on_tracker_state(self,p):
        self.state = p

    def run(self):
        def set_and_send(sc, signal):
            for i in range(0, 3):
                sc.set_signal(signal)
                sc.send_signal()
            return True
            
        with SerialCommander(**self.__sc_kvargs) as sc:
            sc.on_change.append(self.on_tracker_state)
            while not self.stop:
                try:
                    signal = self.__send_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    break
                set_and_send(sc, signal)
                    

    def __enter__(self, *args, **kvargs):
        self.start()
        return self

    def __exit__(self, *args, **kvargs):
        self.stop = True

    # device specific

    @property
    def preconfigured_devices(self):
        return repr(self.__preconfigured_devices)

    def send_raw_signal(self, signal):
        self.__send_queue.put(signal)

    def action(self, device_name, action_name):
        signal = self.__preconfigured_devices.action(device_name, action_name)
        self.send_raw_signal(signal)




if __name__ == "__main__":
    
    with DeviceController(
        port=sys.argv[1],
        baudrate=9600,
        bytesize=8,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=None
    ) as s:
        s.join()

