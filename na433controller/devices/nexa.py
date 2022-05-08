#!/usr/bin/env python3

from ._abstract import DeviceSignalProvider


class Nexa(DeviceSignalProvider):

    def __init__(self):
        DeviceSignalProvider.__init__(
            self,
            name="Nexa",
            fields={
                "house_code": "int",
                "unit": "int",
                "state": "bool",
                "channel": "int",
                "group": "bool",
            }
        )

    def _generate_code(self, **kvargs):
        house_code = kvargs["house_code"]
        unit = kvargs["unit"]
        state = kvargs["state"]
        channel = kvargs["channel"]
        group = kvargs["group"]

        house_code_bin = bin(int(house_code))[2:].rjust(26, "0")
        control_6bit = "".join([ 
            ("1" if group else "0"),
            ("1" if state else "0"),
            bin((int(channel) & 0x03) ^ 0x03)[2:].rjust(2, "0")[-2:],
            bin((int(unit) & 0x03) ^ 0x03)[2:].rjust(2, "0")[-2:]
        ])

        plaincode = house_code_bin + control_6bit

        manchestered = "".join(['01' if '1' == e else '10' for e in plaincode])
        return manchestered.encode("ascii")



if __name__ == "__main__":
    nexa = Nexa()
    print(repr(nexa))

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("house_code", type=int)
    parser.add_argument("unit", type=int)
    parser.add_argument("--channel", type=int, default=0)
    parser.add_argument("--group", action="store_true", default=False)
    parser.add_argument("state", choices=["on", "off"])

    args = parser.parse_args()

    print(Nexa()(
        house_code=args.house_code, 
        unit=args.unit,
        group=args.group,
        state=("on" == args.state),
        channel=args.channel
    ))
