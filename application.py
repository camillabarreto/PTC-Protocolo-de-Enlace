#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import sys


class Application(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)

        # a conexão com as camadas adjacentes deve ser aqui?

    def handle(self):
        '''Trata o evento associado a este callback. Tipicamente 
        deve-se ler o fileobj e processar os dados lidos'''

        l = sys.stdin.readline()
        print('Lido:', l)

    def send(self, dados: bytes):
        '''Trata o ENVIO de octetos para a camada inferior'''
        print('Application: send')

    def receive(self):
        '''Trata o RECEBIMENTO de octetos da camada inferior'''
        print('Application: receive')
