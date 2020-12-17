#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import sys

'''A subcamada Application é responsável por transmitir
e receber mensagens do usuário. Na transmissão (def handle) 
serão lidos octetos da entrada padrão e enviados para a subcamada 
inferior. Na recepção (def receive) a mensagem será decodificada 
e apresentada na saída padrão. '''

class Application(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)

    def handle(self):
        '''Recebe os octetos do teclado e envia 
        para a camada inferior'''

        msg = sys.stdin.buffer.readline()
        self.lowerLayer.send(msg)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior
        e apresenta no terminal '''
        # msg = msg[:-1]
        print('mensagem: ', msg.decode('utf-8'))
