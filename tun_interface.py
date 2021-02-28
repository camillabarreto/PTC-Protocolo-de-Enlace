#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
from frame import Frame
from tun import Tun
import sys

'''Adicionar descrição'''

class Tun_Interface(Sublayer):

    def __init__(self, tun, tout):
        Sublayer.__init__(self, tun.fd, tout)
        self.tun = tun

    def handle(self):
        '''Adicionar descrição'''
        proto,pkg = self.tun.get_frame() # tun visualiza o usuário como origem
        # print("proto: ", proto)
        # print("pkg: ", pkg)
        self.lowerLayer.send(pkg, proto)

    def receive(self, msg, proto):
        '''Adicionar descrição'''
        self.tun.send_frame(msg, proto) # tun visualiza o usuário como destino