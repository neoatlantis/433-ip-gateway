#!/usr/bin/env python3

import json

class DeviceSignalProvider:

    """Driver for each device. Generates codes based on device-specific
    arguments."""

    def __init__(self, name, fields):
        self.fields = fields
        self.name = name

    def __repr__(self):
        return json.dumps({
            "name": self.name,
            "fields": self.fields
        })

    def _generate_code(self, **kvargs):
        raise NotImplementedError("Must implement this.")

    def __call__(self, **kvargs):
        def raise_error(field_name):
            raise ValueError("%s: invalid value for [%s]." % (
                self.name, field_name))

        # check argument validity
        for arg_key in self.fields:
            if not arg_key in kvargs:
                raise ValueError("%s: must provide value for `%s`" % (
                    self.name, arg_key))
            arg_spec = self.fields[arg_key]

            act_val = kvargs[arg_key]
            act_type = type(act_val)

            if (
                (arg_spec == "bool" and type(act_val) != bool) or
                (arg_spec == "int" and type(act_val) != int)
            ):
                raise_error(arg_key)

        return self._generate_code(**kvargs)


class AbstractDevice:

    """An actionable device. """


