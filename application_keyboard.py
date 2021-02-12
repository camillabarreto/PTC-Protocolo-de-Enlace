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

# Frame size limit
MAX_BYTES = 128


class ApplicationKeyboard(Sublayer):

    def __init__(self, file, tout: float):
        Sublayer.__init__(self, file, tout)
        self.f = file
        self.disable_timeout()

    def handle(self):
        '''Lê os octetos do arquivo e envia 
        para a camada inferior '''
        
        msg = sys.stdin.buffer.readline()
        self.lowerLayer.send(msg)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior
        e apresenta no terminal '''
    
        print('mensagem: ', msg)