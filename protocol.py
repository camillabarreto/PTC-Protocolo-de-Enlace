#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
#from Communicator import Communicator
from serial import Serial


class CallbackStdin(poller.Callback):

    def __init__(self, tout, serial):
        Callback.__init__(self, sys.stdin, tout)

    def handle(self):
        msg = sys.stdin.readline()
        msg = msg.encode('ascii')
        n = serial.write(msg)
        print(msg)

        print('Enviou %d bytes' % n)
        # sys.stdout.flush()

    def handle_timeout(self):
        print('Timeout !')


class CallbackReception(poller.Callback):

    t0 = time.time()

    def __init__(self, tout, c):
        poller.Callback.__init__(self, serial, tout)

    def handle(self):
        msg = ''
        msg = serial.read().decode()
        print('msg: ', msg.encode('ascii'))

    def handle_timeout(self):
        print('Timer: t=', time.time()-CallbackReception.t0)


if __name__ == '__main__':
    path = sys.argv[1]
    rate = 9600
    try:
        serial = Serial(path, rate)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    cb = CallbackStdin(50, serial)
    rx = CallbackReception(50, serial)
    sched = poller.Poller()

    sched.adiciona(cb)
    sched.adiciona(rx)

    sched.despache()
