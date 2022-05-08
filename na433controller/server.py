#!/usr/bin/env python3
import json
from bottle import *
from .devices import DEVICES

drivers = json.dumps([json.loads(repr(e[1]())) for e in DEVICES.items()])

def run_server(device_controller):
    
    @get("/status")
    def get_status():
        return json.dumps(device_controller.state)

    @get("/drivers")
    def get_drivers():
        return drivers

    @get("/devices")
    def get_devices():
        return device_controller.preconfigured_devices

    @get("/action/<device_name:re:[0-9a-zA-Z\\-_]+>/<action_name:re:[0-9a-z]+>")
    def call_action(device_name, action_name):
        try:
            device_controller.action(device_name, action_name)
            return json.dumps({ "done": True })
        except Exception as e:
            return abort(400, json.dumps({ "error": str(e) }))



    run(host="localhost", port=10091)
