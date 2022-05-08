#!/usr/bin/env python3

import json
from .nexa import Nexa
from ._abstract import AbstractDevice

DEVICES = {
    "nexa": Nexa,
}


class OnOffDevice(AbstractDevice):
    
    def __init__(self, config):
        AbstractDevice.__init__(self)

        self.name = config["name"]
        self.on_config = config["$on"]
        self.off_config = config["$off"]

        self.on_driver_instance = DEVICES[self.on_config["driver"]]()
        self.off_driver_instance = DEVICES[self.off_config["driver"]]()

    def action(self, action_name):
        """Start an action. Generates a signal code as return."""
        if action_name == "on":
            return self.on_driver_instance(**self.on_config)
        elif action_name == "off":
            return self.off_driver_instance(**self.off_config)
        else:
            raise Exception("Unsupported action.")

    def __repr__(self):
        return json.dumps({
            "type": "on-off",
            "name": self.name,
            "actions": ["on", "off"],
        })



class PreconfiguredDevices:

    def __init__(self, config):
        # make sure all devices have unique names
        names = list(set([e for e in [e["name"] for e in config] if e]))
        if len(names) != len(config):
            raise Exception("Device names must be unique.")

        self.__devices = {}

        for device_config in config:
            self.__parse_device_config(device_config)

    def __parse_device_config(self, dc):
        if dc["type"] == "on-off":
            self.__devices[dc["name"]] = OnOffDevice(config=dc)
        else: 
            raise Exception("Unknown device type: %s" % dc["type"])

    def __repr__(self):
        ret = {}
        for name in self.__devices:
            ret[name] = json.loads(repr(self.__devices[name]))
        return json.dumps(ret)

    def action(self, device_name, action_name):
        return self.__devices[device_name].action(action_name)
