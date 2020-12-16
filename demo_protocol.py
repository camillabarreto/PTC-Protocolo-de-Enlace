#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
from serial import Serial
from application import Application
from framing import Framing


if __name__ == '__main__':
    path = sys.argv[1]
    rate = 9600
    try:
        serial = Serial(path, rate)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    ap = Application(sys.stdin, 1)
    fr = Framing(serial, 1)

    ap.connect(fr, None)
    fr.connect(None, ap)

    sched = poller.Poller()

    sched.adiciona(ap)
    sched.adiciona(fr)

    sched.despache()
