
class Header:
    
    def __init__(self):
        self.seq # ARQ usa na recepção 
        self.frame_type  # ARQ usa na recepção
        self.id_proto  # ARQ usa na recepção
        self.msg  # ARQ usa na recepção
        self.reservado = 0x00
        self.header = bytearray()
    
    def get_data_frame(self, seq, id_proto, msg):
        if seq == 0: control = 0x00
        else: control = 0x08
        self.header.append(control)
        self.header.append(self.reservado)
        self.header.append(id_proto)
        self.header.append(msg)
        return self.header
    
    def get_ack_frame(self, seq):
        if seq == 0: control = 0x80
        else: control = 0x88
        self.header.append(control)
        self.header.append(self.reservado)
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
