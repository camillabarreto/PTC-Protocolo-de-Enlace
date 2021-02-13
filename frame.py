#!/usr/bin/env python3

MAX_BYTES = 128

class Frame:

    def __init__(self):
        self.seq = 0  # ARQ usa na recepção
        self.frame_type = 0  # ARQ usa na recepção
        self.id_proto = 0x00  # ARQ usa na recepção
        self.msg = b''  # ARQ usa na recepção
        self.reserved = 0x00
        self.header = bytearray()

    def get_data_frame(self, seq, id_proto, msg):
        if seq == 0:
            control = 0x00
        else:
            control = 0x08
        self.header.append(control)
        self.header.append(self.reserved)
        self.header.append(id_proto)
        for byte in msg:
            self.header.append(byte)
        return self.header

    def get_ack_frame(self, seq):
        if seq == 0:
            control = 0x80
        else:
            control = 0x88
        self.header.append(control)
        self.header.append(self.reserved)
        return self.header

    def detach_frame(self, byte_frame):
        control = byte_frame[0]
        if control == 0x00:
            self.seq = 0
            self.frame_type = 0
            self.id_proto = byte_frame[2]
            self.msg = byte_frame[3:]
        elif control == 0x08:
            self.seq = 1
            self.frame_type = 0
            self.id_proto = byte_frame[2]
            self.msg = byte_frame[3:]
        elif control == 0x80:
            self.seq = 0
            self.frame_type = 1
        elif control == 0x88:
            self.seq = 1
            self.frame_type = 1
            
    @property
    def seq(self):
        return self.seq

    @property
    def frame_type(self):
        return self.frame_type

    @property
    def id_proto(self):
        return self.id_proto

    @property
    def msg(self):
        return self.msg
    
    @seq.setter   
    def seq(self, seq):
        if not seq:
            self.header[0] &= 0xf7
        else:
            self.header[0] |= 0x08
    
    @frame_type.setter
    def frame_type(self, vl):
        if not vl:
            self.header[0] &= 0x7f
        else: 
            self.header[0] |= 0x80
            
    @id_proto.setter
    def id_proto(self, id):
        if id == 4: # IPV4
            self.header[2] = 0x800
        elif id == 6: # IPV6
            self.header[2] = 0x866d
        
    @msg.setter
    def msg(self, m):
        self.header[2]
