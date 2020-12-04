#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
#from Communicator import Communicator
from serial import Serial

# States
IDLE = 0
READ = 1
ESCAPE = 2

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }

class CallbackStdin(poller.Callback):

    def __init__(self, tout, serial):
        Callback.__init__(self, sys.stdin, tout)

    def handle(self):        
        msg = sys.stdin.buffer.readline()  # Envia a msg para o Enquadramento para ele enviar pela porta serial
        msg = msg[:-1] # Tirando o '/n' do final da mensagem lida
        frame = bytearray()
        frame.append(FLAG)  # FLAG de inicio

        for byte in msg:
            if (byte == FLAG or byte == ESC):  # 7E -> 5E (^) / 7D -> ?(])
                xor = byte ^ 0x20
                frame.append(ESC)
                frame.append(xor)
            else:
                frame.append(byte)

        frame.append(FLAG)  # FLAG de fim
        serial.write(frame)
        print('Enviou: ', frame)

    def handle_timeout(self):
        print('Timeout !')


class CallbackReception(poller.Callback):

    t0 = time.time()

    def __init__(self, tout, c):
        poller.Callback.__init__(self, serial, tout)

    def handle(self):
        msg = ''
        msg = serial.read().decode()
        print('Recebido: ', msg.encode('ascii'))

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

