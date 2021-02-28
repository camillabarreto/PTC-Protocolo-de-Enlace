#!/usr/bin/env python3

class Frame:

    def __init__(self):
        self.seq = 0
        self.type = 0
        self.id_proto = 0x00
        self.msg = b''
        self.reservado = 0x00
        self.header = bytearray()


    def get_data_frame(self, seq, id_proto, msg):
        self.header.clear()
        self.seq = seq
        self.id_proto = id_proto
        self.msg = msg

        if seq == 0:
            control = 0x00
        else:
            control = 0x08
        self.header.append(control)
        self.header.append(self.reservado)
        self.header.append(self.id_proto)
        for byte in msg:
            self.header.append(byte)

    def get_ack_frame(self, seq):
        self.header.clear()
        if seq == 0:
            control = 0x80
        else:
            control = 0x88
        self.header.append(control)
        self.header.append(self.reservado)

    def detach_frame(self, byte_frame):
        self.header.clear()
        control = byte_frame[0]
        if control == 0x00:
            self.seq = 0
            self.type = 0
            self.id_proto = byte_frame[2]
            self.msg = byte_frame[3:]

            self.header.append(control)
            self.header.append(self.reservado)
            self.header.append(self.id_proto)
            for byte in self.msg:
                self.header.append(byte)

        elif control == 0x08:
            self.seq = 1
            self.type = 0
            self.id_proto = byte_frame[2]
            self.msg = byte_frame[3:]

            self.header.append(control)
            self.header.append(self.reservado)
            self.header.append(self.id_proto)
            for byte in self.msg:
                self.header.append(byte)

        elif control == 0x80:
            self.seq = 0
            self.type = 1

            self.header.append(control)
            self.header.append(self.reservado)

        elif control == 0x88:
            self.seq = 1
            self.type = 1

            self.header.append(control)
            self.header.append(self.reservado)
