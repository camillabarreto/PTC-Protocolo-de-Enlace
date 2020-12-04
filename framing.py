#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial

# States
IDLE = 0
READ = 1
ESCAPE = 2

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }

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
        
        frame = bytearray()
        frame.append(FLAG)  # FLAG de inicio

        for byte in dados:
            if (byte == FLAG or byte == ESC):  # 7E -> 5E (^) / 7D -> ?(])
                xor = byte ^ 0x20
                frame.append(ESC)
                frame.append(xor)
            else:
                frame.append(byte)

        frame.append(FLAG)  # FLAG de fim
        self.dev.write(bytes(frame))

