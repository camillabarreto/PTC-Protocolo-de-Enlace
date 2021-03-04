#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import crc
from frame import Frame

# States
IDLE = 0
INIT = 1
READ = 2
ESCAPE = 3

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }

# Frame size limit
MAX_BYTES = 1024

# Background Colors
# RED = '\033[41m'
# YELLOW = '\033[43m'
# GREEN = '\033[42m'
# BLUE = '\033[44m'
# RST = '\033[0;0m'

# Letter Colors
RED = '\033[31m'
YELLOW = '\033[33m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RST = '\033[0;0m'

'''A subcamada Framing é resposável por tratar as transmissões
e recepções de octetos pela porta serial através do mecanismo de sentinela.
Na transmissão (def send) será anexado aos octetos um valor de FCS
e realizado o enquadramento. Na recepção (def handle) será feito o desenquadramento,
checagem da integridade dos octetos e remoção do valor de FCS. A recepção será 
interrompida e os octetos serão descartados quando ocorrer 
TIMEOUT (def handle_timeout) ou OVERFLOW'''


class Framing(Sublayer):
    def __init__(self, serial_port: Serial, tout: float):
        Sublayer.__init__(self, serial_port, tout)
        self.buffer = bytearray()
        self.disable_timeout()
        self.current_state = IDLE
        self.switch = {
            IDLE: self.idle,
            INIT: self.init,
            READ: self.read,
            ESCAPE: self.escape
        }

    def handle(self):
        '''Recebe byte pela porta serial e repassa à FSM fazer o tratamento 
        pertinente ao estado em que se encontra'''
        byte = self.fd.read()  # Lendo 1 octeto da porta serial
        result = self.FSM(byte)  # FSM retorna True para recepção bem sucedida
        if (result):
            frame_teste = Frame()
            frame_teste.detach_frame(bytes(self.buffer))
            self.upperLayer.receive(frame_teste)
            self.buffer.clear()

    def handle_timeout(self):
        '''Ao atingir um limite de espera pelo próximo byte
        os dados do buffer são descartados e se aguarda pelo próximo frame'''
        self.buffer.clear()
        self.current_state = IDLE
        self.disable_timeout()
        print(YELLOW+'TIMEOUT!'+RST+' Enquadramento')

    def FSM(self, byte):
        func = self.switch[self.current_state]
        return func(byte)

    def idle(self, byte):
        if (byte[0] == FLAG):
            self.current_state = INIT
            self.enable_timeout()

    def init(self, byte):
        if (byte[0] == FLAG):
            self.current_state = INIT

        elif (byte[0] == ESC):
            self.current_state = ESCAPE

        elif (len(self.buffer) < MAX_BYTES):
            self.buffer.append(byte[0])
            self.current_state = READ

        else:
            print(BLUE+'1 OVERFLOW!'+RST+' A mensagem tem mais que', MAX_BYTES, 'bytes.')
            self.buffer.clear()
            self.current_state = IDLE
            self.disable_timeout()
        
        self.reload_timeout()

    def read(self, byte):
        if (byte[0] == FLAG):
            self.current_state = IDLE
            self.disable_timeout()
            fcs = crc.CRC16(self.buffer)

            if fcs.check_crc():
                self.buffer = self.buffer[:-2]
                return True

            else: 
                self.buffer.clear()
                print(RED+'DETECÇÃO DE ERRO!'+RST)

        elif (byte[0] == ESC):
            self.current_state = ESCAPE

        elif (len(self.buffer) < MAX_BYTES):
            self.buffer.append(byte[0])
            self.current_state = READ
        
        else:
            print(BLUE+'2 OVERFLOW!'+RST+' A mensagem tem mais que', len(self.buffer), 'bytes.')
            self.buffer.clear()
            self.current_state = IDLE
            self.disable_timeout()
        
        self.reload_timeout()

    def escape(self, byte):
        if (byte[0] == FLAG or byte[0] == ESC):
            self.buffer.clear()
            self.disable_timeout()
            self.current_state = IDLE

        elif (len(self.buffer) < MAX_BYTES):
            byte = byte[0] ^ 0x20
            self.buffer.append(byte)
            self.current_state = READ

        else:
            print(BLUE+'3 OVERFLOW! A mensagem tem mais que', MAX_BYTES, 'bytes.'+RST)
            self.buffer.clear()
            self.current_state = IDLE
            self.disable_timeout()

        self.reload_timeout()

    def send(self, fr):
        '''Recebe octetos da camada superior, anexa dados de verificação de erro,
        realiza o preenchimento de byte e envia pela porta serial'''

        fcs = crc.CRC16(fr.header)
        fr.header = fcs.gen_crc()

        frame = bytearray()
        frame.append(FLAG)

        for byte in fr.header:
            if (byte == FLAG or byte == ESC):
                xor = byte ^ 0x20
                frame.append(ESC)
                frame.append(xor)

            else:
                frame.append(byte)

        frame.append(FLAG)
        self.fd.write(bytes(frame))  # Envia mensagem pela porta serial
