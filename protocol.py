#!/usr/bin/env python3

import poller
import sys
import time
from poller import Callback
from serial import Serial

# States
IDLE = 0
INIT = 1
READ = 2
ESCAPE = 3

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }


class CallbackStdin(poller.Callback):

    def __init__(self, tout, serial):
        Callback.__init__(self, sys.stdin, tout)

    def handle(self):
        # Envia a msg para o Enquadramento para ele enviar pela porta serial
        msg = sys.stdin.buffer.readline()
        msg = msg[:-1]  # Tirando o '/n' do final da mensagem lida
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
    current_state = IDLE

    def __init__(self, tout, c):
        poller.Callback.__init__(self, serial, tout)
        self.n = 0  # Quantidade de bytes recebidos
        self.frame = bytearray()

    def handle(self):
        msg = serial.read()
        msg = msg.hex()
        msg = int(msg, 16)

        '''Descomentar a próxima linha para chamar a máquina de estados -> FSM(octeto)
           Os métodos correspondentes aos estados não estão implementados, existindo 
           apenas um fluxo de mudança de estado para visualizar o funcionamento da FSM.
        '''

        frame = self.FSM(msg)
        print('Recebido: ', frame)

    def handle_timeout(self):
        print('Timer: t=', time.time() - CallbackReception.t0)

    def FSM(self, byte):
        switch = {
            IDLE: self.idle,
            INIT: self.init,
            READ: self.read,
            ESCAPE: self.escape
        }
        func = switch.get(self.current_state, lambda: None)
        return func(byte)

    def idle(self, byte):
        print('IDLE')
        print(byte)
        if (byte == FLAG):
            self.n = 0
            print('idle -> init')
            self.current_state = INIT

    def init(self, byte):
        if (byte == FLAG):
            self.current_state = INIT
        elif (byte == ESC):
            self.current_state = ESCAPE
        else:
            self.frame.append(byte)
            self.n += 1
            self.current_state = READ

        print('init -> read')

    def read(self, byte):
        if (byte == FLAG):
            self.current_state = IDLE
            return self.frame

        elif (byte == ESC):
            self.current_state = ESCAPE

        # se TIMEOUT
        # descarta quadro
        # self.current_state = IDLE

        else:
            self.frame.append(byte)
            self.n += 1
            self.current_state = READ

        print('read -> idle')

    def escape(self, byte):
        if (byte == FLAG):  # se FLAG ou TIMEOUT
            self.frame.clear()
            self.current_state = IDLE

        else:
            byte = byte ^ 0x20
            self.frame.append(byte)
            self.n += 1
            print('escape')
            self.current_state = READ


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
