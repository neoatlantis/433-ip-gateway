#!/usr/bin/env python3

import os
import sys
import serial
import time
import threading
from nexa import nexa

with serial.Serial(
    port=sys.argv[1],
    baudrate=9600,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=None
) as s:

    while not s.is_open:
        time.sleep(0.5)
        print("Waiting port open...")

    time.sleep(0.5)

    s.read_all()

    s.flushInput()
    s.flushOutput()

    send_buffer=nexa(house_code=sys.argv[2], unit=sys.argv[3], state=sys.argv[4])

    for i in range(0, 5): s.write(b"\n")

    while True:
        s.write(b"#random\n")
        s.write(b"?\n\r")
        time.sleep(1)
        print(s.read_all().decode("ascii"))
        time.sleep(1)
        s.write(b"+" + send_buffer + b"\n")
        print(s.read_all().decode("ascii"))
        time.sleep(1)
        s.write(b">\n")
        print(s.read_all().decode("ascii"))

    s.write(b"+" + send_buffer + b"\r")
    s.flush()
    
    print(s.readline())
    s.flush()
