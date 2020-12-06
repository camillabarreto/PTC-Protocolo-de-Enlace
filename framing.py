#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial

# States
IDLE = 0
READ = 1
ESCAPE = 2

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }


class Framing(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)

        # a conexão com as camadas adjacentes deve ser aqui?

    def handle(self):
        '''Trata o evento associado a este callback. Tipicamente 
        deve-se ler o fileobj e processar os dados lidos'''
        o = self.fd.readline()
        self.receive(o)

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        print('Framing: handle_timeout')

    def send(self, msg):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a porta serial'''
        print('Framing: send')
        self.fd.write(msg)

    def receive(self, o):
        '''Recebe os octetos da porta serial, trata os dados
        e envia para a camada superior'''
        print('Framing: receive')
        self.upperLayer.receive(o)
