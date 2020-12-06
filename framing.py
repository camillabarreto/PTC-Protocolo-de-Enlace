#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial

# States
IDLE = 0
INIT = 1
READ = 2
ESCAPE = 3

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }


class Framing(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)
        self.frame = bytearray()
        self.current_state = IDLE
        self.n = 0  # Quantidade de bytes recebidos

        # a conexão com as camadas adjacentes deve ser aqui?

    def handle(self):
        '''Trata o evento associado a este callback. Tipicamente 
        deve-se ler o fileobj e processar os dados lidos'''

        o = self.fd.read()
        self.receive(o)

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        # Limpa o buffer se ocorrer timeout
        self.frame.clear()
        print('Framing: handle_timeout')

    def send(self, msg):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a porta serial'''
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
        self.fd.write(bytes(frame))
        print('Framing: send', frame)

    def receive(self, msg):
        '''Recebe os octetos da porta serial, trata os dados
        e envia para a camada superior'''
        msg = msg.hex()
        msg = int(msg, 16)

        result = self.FSM(msg)

        if (result != None):
            self.upperLayer.receive(bytes(self.frame))  # envia o conteúdo lido para a camada superior
            print('Framing: receive', self.frame)
            self.frame.clear()

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
            print('read -> idle')
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
