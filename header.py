#!/usr/bin/env python3

class Header():
    def __init__(self):
        self.control
        self.reserved = 0x00
        self.id_proto # número definido pela app
        self.msg
        self.fcs
        self.header = bytearray()
        
    def detach_frame(self, frame): # Recebe a msg e divide os campos de acordo
        self.control = frame[0]
        if(self.control == 0x00 or self.control == 0x08): # o header tem id_proto apenas se tipo data (bit7 = 0)
            self.id_proto = frame[2]
            self.msg = frame[3]
        # self.fcs = ? O Enquadramento já retirou esse campo
        
    def get_frame(self, seq, id_proto, msg): # Envia o quadro com o cabeçalho anexado à mensagem
        if(seq == 0):
            self.control = 0x00
        else:
            self.control = 0x08
        self.id_proto = id_proto
        self.msg = msg
        self.header.append(self.control)
        self.header.append(self.reserved)
        self.header.append(self.id_proto)
        self.header.append(self.msg)
        # self.header.append(self.fcs)
        return self.header
        
    def send_ack(self, seq):
        if(seq == 0):
            self.control = 0x80
        else:
            self.control = 0x88
        self.header.append(self.control)
        self.header.append(self.reserved)
        # self.header.append(self.fcs)
        return self.header
        
    def get_control(self):
        return self.control
        
        
