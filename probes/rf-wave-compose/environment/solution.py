import numpy as np
import skrf as rf


def compose(left, right):
    """Connect left port 2 to right port 1 and return 50-ohm power-wave S."""
    f=rf.Frequency.from_f(left['frequency_hz'],unit='hz')
    a=rf.Network(frequency=f,s=left['s'],z0=50)
    b=rf.Network(frequency=f,s=right['s'],z0=50)
    return (a**b).s
