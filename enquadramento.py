#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
from serial import Serial
import enum

# States
IDLE = 0
READ = 1
ESCAPE = 2

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }


class CallbackStdin(poller.Callback):

    def __init__(self, tout, s):
        Callback.__init__(self, sys.stdin, tout)
        self.serial = s

    def handle(self):  # Será um método def envia(self, msg) chamado pelo handle da Aplicação
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
        self.transmitter(frame)

    def handle_timeout(self):
        print('Timeout !')

    def transmitter(self, msg):
        self.serial.write(msg)
        print('Enviou: ', msg)


class CallbackReception(poller.Callback):
    t0 = time.time()

    def __init__(self, tout, s):
        poller.Callback.__init__(self, s, tout)
        self.serial = s
        self.frame = bytearray()

    def handle(self):
        self.frame = self.receiver()
        print('Recebido: ', self.frame)

    def handle_timeout(self):
        print('Timer: t=', time.time() - CallbackReception.t0)

    def receiver(self):
        msg = self.serial.read()
        # Notifica a Aplicação de que chegou mensagem pela serial e ela mostra no terminal
        return msg

    '''
    def handle_state(self):
    '''


if __name__ == '__main__':
    try:
        s = Serial(sys.argv[1], 9600)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    cb = CallbackStdin(30, s)
    rx = CallbackReception(35, s)
    sched = poller.Poller()

    sched.adiciona(cb)
    sched.adiciona(rx)

    sched.despache()
