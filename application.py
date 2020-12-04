#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import sys


class Application(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)

    def recebe(self, dados: bytes):
        # mostra na tela os dados recebidos da subcamada inferior
        print('RX:', dados)

    def handle(self):
        # lê uma linha do teclado
        dados = sys.stdin.readline()

        # converte para bytes ... necessário somente
        # nesta aplicação de teste, que lê do terminal
        dados = dados.encode('utf8')

        # envia os dados para a subcamada inferior (self.lower)
        self.lowerLayer.envia(dados)
