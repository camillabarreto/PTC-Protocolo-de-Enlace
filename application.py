#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import sys


class Application(Sublayer):

    def __init__(self, file, tout: float):
        Sublayer.__init__(self, file, tout)
        self.f = file
        self.msg = bytearray()
        self.i = 0

    def handle(self):
        '''Recebe os octetos do teclado, trata os dados
        e envia para a camada inferior'''
        
        '''
        linha = self.f.readline()
        
        while linha:
            print(linha)
            linha = self.f.readline()
        self.f.close()
        '''
        
        conteudo_arq = self.f.read()
        self.f.close()
        self.disable()
        # print(conteudo_arq)
        self.lowerLayer.send(conteudo_arq)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para o terminal '''
        # msg = msg[:-1]
        print('mensagem: ', msg.decode('utf-8'))
