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
        '''Trata o evento associado a este callback. Tipicamente 
        deve-se ler o fileobj e processar os dados lidos'''

        msg = sys.stdin.buffer.readline()  # Lê em bytes
        msg = msg[:-1]  # Tirando o '/n' do final da mensagem lida
        if len(msg) < 129:
            self.send(msg)
        else:
            print('Mensagem maior que 128 caracteres')

    def send(self, msg):
        '''Recebe os octetos do teclado, trata os dados
        e envia para a camada inferior'''
        print('Application: send')
        self.lowerLayer.send(msg)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para o terminal'''
        print('Application: receive')
        print('mensagem: ', msg)
