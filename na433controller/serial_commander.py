#!/usr/bin/env python3

import os
import sys
import serial
import time
import threading
import queue
import re
import json



class ArduinoStateTracker:

    MAGIC_WORD = "NA433GATEWAY"

    def __init__(self):
        self.last_update = 0
        self.signal_buffer = None
        self.connected = False
        self.signal_sent = False
        self.accepted_signal_bits = None

        self._staged = []
        self._staging_session_id = None

    def feed(self, line):
        try:
            if type(line) == bytes: line = line.decode("ascii")
        except:
            return
        line = line.strip()
        if not line.startswith("#"):
            if self._staging_session_id:
                self._staged.append(line)
            if len(self._staged) > 100:
                self._staging_session_id = None
                self._staged = []
            return
        
        try:
            begin_mark = re.search("begin-cycle-([0-9a-f]+)", line)[1]

            self._staging_session_id = begin_mark
            self._staged = []
        except:
            pass

        try:
            end_mark = re.search("end-cycle-([0-9a-f]+)", line)[1]
            if end_mark == self._staging_session_id:
                self.on_new_state()

                self._staging_session_id = None
                self._staged = []
        except:
            pass

    def on_new_state(self):
        #print(self._staging_session_id, self._staged) 

        self.last_update = time.time()
        self.signal_buffer = None
        self.connected = False
        self.signal_sent = False
        self.accepted_signal_bits = None

        for line in self._staged:
            matched = True

            try:
                if line.startswith("? %s" % self.MAGIC_WORD):
                    splitline = line.split(" ")
                    self.signal_buffer = \
                        line.split(" ")[2] if len(splitline) >= 3 else None

                elif line == ">OK":
                    self.signal_sent = True

                elif line.startswith("+"):
                    self.accepted_signal_bits = int(line[1:])

                else:
                    matched = False

                if matched: self.connected = True

            except Exception as e:
                print(e)
        print(str(self))

    def __str__(self):
        return json.dumps({
            "last_update": self.last_update,
            "signal_buffer": self.signal_buffer,
            "connected": self.connected,
            "signal_sent": self.signal_sent,
            "accepted_signal_bits": self.accepted_signal_bits,
        })



class SerialCommander:

    def __init__(self, **kvargs):
        kvargs["timeout"] = 1
        self.serial_device = serial.Serial(**kvargs)

        self.write_queue = queue.Queue() # write to serial
        self.read_queue = queue.Queue() # read from serial
        self.flag_exit = threading.Event()

    def set_signal(self, signalbuffer):
        if type(signalbuffer) == str:
            signalbuffer = signalbuffer.encode("ascii")
        self.write_queue.put(b"+%s\n" % signalbuffer)

    def send_signal(self):
        self.write_queue.put(b">\n")

    def reset(self):
        self.write_queue.put(b"R\n\r" * 10)

    def _job(self):

        def serial_write_read(data=None):
            try:
                if data:
                    self.serial_device.write(data)
                time.sleep(1)
                readdata = self.serial_device.read_all()
                if readdata:
                    readlines = [
                        e for e in [e.strip() for e in readdata.split(b"\n")]
                        if e
                    ]
                    for l in readlines: self.read_queue.put(l)
            except Exception as e:
                self.flag_exit.set()
                raise e
                
                
        time.sleep(0.5)
        while True:
            if self.flag_exit.is_set(): break
            cycle_id = os.urandom(16).hex().encode("ascii")

            if not self.serial_device.is_open:
                time.sleep(0.5)
                print("Waiting port open...")
                continue

            serial_write_read()

            serial_write_read(b"#begin-cycle-%s\n" % cycle_id)
            serial_write_read(b"?\n\r")
            
            try:
                writedata = self.write_queue.get(timeout=0.1)
                if writedata:
                    serial_write_read(writedata)
            except Exception as e:
                print(e)

            serial_write_read(b"#end-cycle-%s\n" % cycle_id)

    def __enter__(self, *args, **kvargs):
        try:
            self.serial_device.open()
        except:
            pass
        self.job = threading.Thread(target=self._job)
        self.job.start()
        return self

    def __exit__(self, *args, **kvargs):
        self.flag_exit.set()
        self.serial_device.close()


if __name__ == "__main__":

    with SerialCommander(
        port=sys.argv[1],
        baudrate=9600,
        bytesize=8,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=None
    ) as s:

        tracker = ArduinoStateTracker()

        i = 0
        
        while not s.flag_exit.is_set():
            i += 1

            if i == 3:
                s.set_signal("0101010")

            if i == 4:
                s.send_signal()

            if i == 6:
                s.reset()

            try:
                r = s.read_queue.get(timeout=1)
                tracker.feed(r)
            except KeyboardInterrupt as e:
                exit()
            except Exception:
                pass
