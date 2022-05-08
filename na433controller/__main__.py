#!/usr/bin/env python3
import sys

import yaml
import serial

from .device_controller import DeviceController
from .server import run_server

config = yaml.load(open(sys.argv[2], "r").read())
devices_config = config["devices"]


with DeviceController(
    devices_config,

    port=sys.argv[1],
    baudrate=9600,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=None
) as dc:
    run_server(dc)
