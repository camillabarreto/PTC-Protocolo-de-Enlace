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
MAX_BYTES = 128 + 3     # cabeçalhos ARQ: control, id_proto, reservado


'''A subcamada Framing é resposável por tratar as transmissões
e recepções de octetos pela porta serial. Na transmissão (def send) 
será anexado aos octetos um valor de FCS e realizado o enquadramento.
Na recepção (def handle) será feito o desenquadramento, checagem da 
integridade dos octetos e remoção do valor de FCS. A recepção será 
interrompida quando atingir um limite de tempo (def handle_timeout)
e os octetos serão descartados'''


class Framing(Sublayer):

    def __init__(self, serial_port: Serial, tout: float):
        Sublayer.__init__(self, serial_port, tout)
        self.buffer = bytearray()
        self.disable_timeout()
        self.current_state = IDLE

    def handle(self):
        byte = self.fd.read()  # Lendo 1 octeto da porta serial
        result = self.FSM(byte)  # FSM retorna True para recepção bem sucedida
        if (result):
            if (len(self.buffer) <= MAX_BYTES):
                frame_teste = Frame()
                frame_teste.detach_frame(bytes(self.buffer))
                self.upperLayer.receive(frame_teste)
            else:
                print('OVERFLOW! A mensagem tem mais de ', MAX_BYTES, ' bytes.')

            self.buffer.clear()

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        self.buffer.clear()
        self.current_state = IDLE
        self.disable_timeout()
        print('TIMEOUT!')

    def FSM(self, byte):
        switch = {
            IDLE: self.idle,
            INIT: self.init,
            READ: self.read,
            ESCAPE: self.escape
        }
        func = switch.get(self.current_state, lambda: None)
        return func(byte)

    def idle(self, byte):
        if (byte[0] == FLAG):
            self.current_state = INIT
            self.enable_timeout()
            
        return False

    def init(self, byte):
        if (byte[0] == FLAG):
            self.current_state = INIT

        elif (byte[0] == ESC):
            self.current_state = ESCAPE

        else:
            self.buffer.append(byte[0])
            self.current_state = READ

        self.reload_timeout()
        return False

    def read(self, byte):
        if (byte[0] == FLAG):
            self.current_state = IDLE
            self.disable_timeout()
            fcs = crc.CRC16(self.buffer)
            if fcs.check_crc():
                self.buffer = self.buffer[:-2]
                return True
            else: self.buffer.clear()

        elif (byte[0] == ESC):
            self.current_state = ESCAPE

        else:
            self.buffer.append(byte[0])
            self.current_state = READ

        self.reload_timeout()
        return False

    def escape(self, byte):
        if (byte[0] == FLAG or byte[0] == ESC):
            self.buffer.clear()
            self.disable_timeout()
            self.current_state = IDLE

        else:
            byte = byte[0] ^ 0x20
            self.buffer.append(byte)
            self.current_state = READ

        self.reload_timeout()
        return False

    def send(self, fr):
        '''Recebe os octetos da camada superior, trata os dados
        e envia pela porta serial '''

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
