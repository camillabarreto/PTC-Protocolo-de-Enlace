#!/usr/bin/env python3

class Header():
    def __init__(self, control, id_proto, msg, fcs):
        self.control = control
        self.reserved = 0x00
        self.id_proto = id_proto
        self.msg = msg
        self.fcs = fcs
        self.header = bytearray()
        
    def get_header(self):
        self.header.append(self.control)
        self.header.append(self.reserved)
        if(self.control == 0x00 or self.control == 0x08): # o header tem id_proto apenas se tipo data (bit7 = 0)
            self.header.append(self.id_proto)
        self.header.append(self.msg)
        self.header.append(self.fcs)
        return self.header
        
    def get_control(self):
        return self.control
        
    def not_seq(self):
        self.control ^= 0x08
        
    def not_type():
        self.control ^= 0x80
