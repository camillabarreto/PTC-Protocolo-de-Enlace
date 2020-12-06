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
        msg = self.fd.read()
        print('Recebido ', msg)

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        print('Framing: handle_timeout')

    def send(self, dados: bytes):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a porta serial'''
        print('Framing: send')

    def receive(self):
        '''Recebe os octetos da porta serial, trata os dados
        e envia para a camada superior'''
        print('Framing: receive')
