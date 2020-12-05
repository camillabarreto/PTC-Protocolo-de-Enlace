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
        deve-se ler o fileobj e processar os dados lidos. Classes
        derivadas devem sobrescrever este método.'''
        pass

    def handle_timeout(self):
        '''Trata um timeout associado a este callback. Classes
        derivadas devem sobrescrever este método.'''
        pass

    def send(self):
        '''Trata o ENVIO de octetos para a camada superior'''
        pass

    def receive(self):
        '''Trata o RECEBIMENTO de octetos da camada superior'''
        pass

    def connect(self, lower, upper):
        '''Realiza a conexão com as camadas adjacentes'''
        self.lowerLayer = lower
        self.upperLayer = upper
