#!/usr/bin/env python3

import poller
from poller import Callback


class Sublayer(poller.Callback):

    def __init__(self, fd, timeout):
        Callback.__init__(self, fd, timeout)
        self.lowerLayer = None
        self.upperLayer = None

    def handle(self):
        '''Trata o evento associado a este callback. Tipicamente 
        deve-se ler o fileobj e processar os dados lidos'''
        pass

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        pass

    def send(self):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a camada inferior'''
        pass

    def receive(self):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para a camada superior'''
        pass

    def connect(self, lower, upper):
        '''Realiza as conexões com as camadas adjacentes'''
        self.lowerLayer = lower
        self.upperLayer = upper

