#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
from frame import Frame
from tun import Tun
import sys

'''A subcamada Tun_Interface é resposável por fazer a mediação do 
protocolo de enlace e da interface de rede Tun, integrando 
o protocolo desenvolvido com a pilha de protocolos do Linux. 
Na transmissão (def handle) o pacote recebido pela interface Tun é
passado para a camada inferior junto com o protocolo de Rede correspondente.
Na recepção (def receive) o pacote recebido pela camada inferior é entregue
a interface Tun junto com o protocolo de Rede correspondente.'''


class Tun_Interface(Sublayer):

    def __init__(self, tun, tout):
        Sublayer.__init__(self, tun.fd, tout)
        self.disable_timeout()
        self.tun = tun

    def handle(self):
        '''Recebe pacote e seu protocolo pela interface Tun 
        e repassa para a camada inferior'''
        proto,pkg = self.tun.get_frame()
        self.lowerLayer.send(pkg, proto)

    def receive(self, msg, proto):
        '''Recebe da camada inferior um pacote e seu protocolo
        e repassa para a interface Tun'''
        self.tun.send_frame(msg, proto)
