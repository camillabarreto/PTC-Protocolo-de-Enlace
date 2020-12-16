#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import sys


class Application(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)

    def handle(self):
        '''Recebe os octetos do teclado, trata os dados
        e envia para a camada inferior'''

        msg = sys.stdin.buffer.readline()  # Lê em bytes
        msg = msg[:-1]  # Tirando o '/n' do final da mensagem lida
        self.lowerLayer.send(msg)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para o terminal '''
        msg = msg[:-1]
        print('mensagem: ', msg.decode('utf-8'))
