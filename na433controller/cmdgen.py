#!/usr/bin/env python3

def LRC(s):
    ret = 0
    for e in s:
        ret = (ret + e) & 0xFF
    return ((ret ^ 0xFF) + 1) & 0xFF

class WaveformGenerator:

    def __init__(self, pulsewidth):
        assert type(pulsewidth) == int and 0 < pulsewidth <= 0xFFFF
        self.__waveform = []
        self.__pulsewidth = pulsewidth

    def __call__(self, logic_level, duration):
        assert type(logic_level) == bool
        assert type(duration) == int and 1 <= duration <= 8
        self.__waveform.append(logic_level and (duration+7) or (duration-1))

    def generate_serial_command(self):
        payload = "".join(
            [hex(self.__pulsewidth)[2:].rjust(4, "0")] +
            [hex(e)[2:] for e in self.__waveform]
        )
        payload = payload.encode("ascii")
        return payload + hex(LRC(payload))[2:].rjust(2,"0").encode("ascii")






if __name__ == "__main__":
    import sys

    wg = WaveformGenerator(270)
    wg(True, 1)
    wg(False, 5)
    wg(False, 3)
    wg(True, 1)
    wg(False, 1)
    wg(True, 1)
    wg(False, 3)

    print(wg.generate_serial_command())
