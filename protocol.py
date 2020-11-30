#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
from Communicator import Communicator
from serial import Serial


class CallbackStdin(poller.Callback):

    def __init__(self, tout, c):
        Callback.__init__(self, sys.stdin, tout)

    def handle(self):
        msg = sys.stdin.readline()
        c.transmitter(msg)
        #print('Lido:', l)

    def handle_timeout(self):
        print('Timeout !')


class CallbackReception(poller.Callback):

    t0 = time.time()

    def __init__(self, tout, c):
        poller.Callback.__init__(self, c.serial, tout)

    def handle(self):
        msg = ''
        msg = c.receiver()
        print('msg: ', msg.encode('ascii'))

    def handle_timeout(self):
        print('Timer: t=', time.time()-CallbackReception.t0)


if __name__ == '__main__':
    path = sys.argv[1]
    try:
        c = Communicator(path, 9600)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    cb = CallbackStdin(30, c)
    rx = CallbackReception(35, c)
    sched = poller.Poller()

    sched.adiciona(cb)
    sched.adiciona(rx)

    sched.despache()
