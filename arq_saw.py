import poller
from poller import Callback
from sublayer import Sublayer
from frame import Frame

# States
IDLE = 0
WAIT = 1

# ID
SEND = 0
RECEIVE = 1

# FRAME TYPES
DATA = 0
ACK = 1

class ARQ_saw(Sublayer):

    def __init__(self, porta_serial, tout):
        Sublayer.__init__(self, porta_serial, tout)
        self.disable_timeout()
        self.current_state = IDLE
        self.rx = 0 # se trocar pra 1 da pra testar ACK NOT RX
        self.tx = 0
        self.id_proto = 0x11
        self.f = Frame()
    
    def send(self, data):
        '''Adicionar descrição '''

        self.f.get_data_frame(self.tx, self.id_proto, data)
        self.FSM(SEND, self.f)

    def receive(self, frame):
        '''Adicionar descrição '''
        
        fs = Frame()
        fs.detach_frame(frame)
        self.FSM(RECEIVE, fs)
    
    def FSM(self, id, f):
        switch = {
            IDLE: self.idle,
            WAIT: self.wait
        }

        # Executa a função do estado atual
        func = switch.get(self.current_state, lambda: None)
        return func(id, f)

    def idle(self, id, f):
        # print('IDLE - ARQ')

        if id == SEND and f.frame_type == DATA:
            # print('ENVIO DATA: ', f.header)
            self.lowerLayer.send(f.header)
            self.current_state = WAIT

        elif id == RECEIVE and f.frame_type == DATA:
            # print('RECEBE DATA', f.header)
            if f.seq == self.rx:
                self.upperLayer.receive(f.msg)
                f.get_ack_frame(self.rx)
                self.rx = abs(self.rx - 1)
            else:
                f.get_ack_frame(f.seq)
            # print('ENVIO ACK', f.header)
            self.lowerLayer.send(f.header)


    def wait(self, id, f):
        # print('WAIT - ARQ')

        if id == RECEIVE and f.frame_type == DATA:
            # print('RECEBE DATA', f.header)
            if f.seq == self.rx:
                self.upperLayer.receive(f.msg)
                f.get_ack_frame(self.rx)
                self.rx = abs(self.rx - 1)
            else:
                f.get_ack_frame(f.seq)
            # print('ENVIO ACK', f.header)
            self.lowerLayer.send(f.header)

        elif id == RECEIVE and f.frame_type == ACK:
            # print('RECEBE ACK', f.header)
            self.tx = abs(self.tx - 1)
            self.current_state = IDLE

        # ainda precisa implementar TIMEOUT
