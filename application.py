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

class Application(Sublayer):

    def __init__(self, file, tout: float):
        Sublayer.__init__(self, file, tout)
        self.f = file

    def handle(self):
        '''Recebe os octetos do teclado e envia 
        para a camada inferior'''

        i = 0
        msg = ''
        while (i < MAX_BYTES):
            msg += self.f.readline(1)  # Lê 1 caractere
            # print(len(msg))
            i += 1

        if(msg == ''):  # Se chegou ao final do arquivo
            self.f.close()
            self.disable()
        else:
            print('Transmitiu ', len(msg), ' bytes')
            self.lowerLayer.send(msg)

    def receive(self, msg):
        '''Recebe os octetos da camada inferior
        e apresenta no terminal '''
        # msg = msg[:-1]
        print('mensagem: ', msg.decode('utf-8'))
