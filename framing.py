#!/usr/bin/env python3

import poller
from poller import Callback
from sublayer import Sublayer
from serial import Serial
import crc

# States
IDLE = 0
INIT = 1
READ = 2
ESCAPE = 3

# Special
FLAG = 0x7E  # ~
ESC = 0x7D  # }

# Frame size limit
MAX_BYTES = 128


'''A subcamada Framing é resposável por tratar as transmissões
e recepções de octetos pela porta serial. Na transmissão (def send) 
será anexado aos octetos um valor de FCS e realizado o enquadramento.
Na recepção (def handle) será feito o desenquadramento, checagem da 
integridade dos octetos e remoção do valor de FCS. A recepção será 
interrompida quando atingir um limite de tempo (def handle_timeout)
e os octetos serão descartados'''


class Framing(Sublayer):

    def __init__(self, porta_serial: Serial, tout: float):
        Sublayer.__init__(self, porta_serial, tout)
        self.msg = bytearray()  # buffer
        self.disable_timeout()
        self.current_state = IDLE

    def handle(self):
        byte = self.fd.read()  # Lendo 1 octeto da porta serial
        result = self.FSM(byte)  # FSM retorna True para recepção bem sucedida

        if (result):
            if (len(self.msg) <= MAX_BYTES):
                self.upperLayer.receive(bytes(self.msg)) # Envia mensagem para subcamada superior

            else:
                print('OVERFLOW! A mensagem tem ', len(self.msg), ' bytes.')

            self.msg.clear()

    def handle_timeout(self):
        '''Trata um timeout associado a este callback'''
        self.msg.clear()
        self.current_state = IDLE
        self.disable_timeout()

    def FSM(self, byte):
        switch = {
            IDLE: self.idle,
            INIT: self.init,
            READ: self.read,
            ESCAPE: self.escape
        }

        func = switch.get(self.current_state, lambda: None) # Executa a função do estado atual
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
            self.msg.append(byte[0])
            self.current_state = READ

        self.reload_timeout()
        return False

    def read(self, byte):
        if (byte[0] == FLAG):
            self.current_state = IDLE
            self.disable_timeout()
            fcs = crc.CRC16(self.msg)

            if fcs.check_crc():
                self.msg = self.msg[:-2]
                return True

        elif (byte[0] == ESC):
            self.current_state = ESCAPE

        else:
            self.msg.append(byte[0])
            self.current_state = READ

        self.reload_timeout()
        return False

    def escape(self, byte):
        if (byte[0] == FLAG or byte[0] == ESC):
            self.msg.clear()
            self.current_state = IDLE

        else:
            byte = byte[0] ^ 0x20
            self.msg.append(byte)
            self.current_state = READ

        self.reload_timeout()
        return False

    def send(self, msg):
        '''Recebe os octetos da camada superior, trata os dados
        e envia pela porta serial'''

        fcs = crc.CRC16(msg)
        
        frame = bytearray()

        if (len(msg) <= MAX_BYTES):
            msg = fcs.gen_crc()  # Anexa na mensagem o valor de FCS

            # GERAR ERROR PROPOSITAIS NA TRANSMISSÃO
            # msg = msg[:-1] # remove o ultimo byte
            # msg.reverse() # inverte os bytes
            # msg[0] = 99  # alterando o primeiro byte
            
            frame.append(FLAG)

            for byte in msg:
                if (byte == FLAG or byte == ESC):
                    xor = byte ^ 0x20
                    frame.append(ESC)
                    frame.append(xor)

                else:
                    frame.append(byte)

            frame.append(FLAG)
            self.fd.write(bytes(frame)) # Envia mensagem pela porta serial

        else:
            print('OVERFLOW! A mensagem tem ', len(msg), ' bytes.')

