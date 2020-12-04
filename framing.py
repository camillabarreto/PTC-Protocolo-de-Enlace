#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial


class Framing(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)
        # dev: este atributo mantém uma referência à porta serial
        self.dev = porta_serial
        # buffer: este atributo armazena octetos recebidos
        self.buffer = bytearray()

    def handle(self):
        # lê um octeto da serial, e o armazena no buffer
        # Encaminha o buffer para camada superior, se ele tiver 8 octetos
        octeto = self.dev.read(1)
        self.buffer += octeto
        if len(self.buffer) == 8:
            # envia o conteúdo do buffer para a camada superior (self.upper)
            self.upperLayer.recebe(bytes(self.buffer))
            self.buffer.clear()

    def handle_timeout(self):
        # Limpa o buffer se ocorrer timeout
        self.buffer.clear()
        print('timeout no enquadramento em', self.timeout.time())

    def envia(self, dados: bytes):
        # Apenas envia os dados pela serial
        # Este método é chamado pela subcamada superior
        quadro = bytearray()
        quadro.append(0x7e)
        quadro += dados
        quadro.append(0x7e)
        self.dev.write(bytes(quadro))
