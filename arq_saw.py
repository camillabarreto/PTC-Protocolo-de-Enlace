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
        self.rx = 0
        self.tx = 0
        self.id_proto = 0x11
        self.f = Frame()
    
    def send(self, data):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a camada inferior '''
        
        # esta certo armazenar a ultima instancia de Frame transmitida, 
        # pq pode ser que precisa retransmitir

        self.f.get_data_frame(self.tx, self.id_proto, data)
        print('ENVIO: ', self.f.header)
        self.FSM(SEND, self.f)

    def receive(self, frame):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para a camada superior '''
        
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
        if id == SEND:
            self.lowerLayer.send(f.header)
            self.current_state = WAIT
        elif f.frame_type == DATA:
            self.upperLayer.receive(f.msg)
            f.get_ack_frame(self.rx)
            self.lowerLayer.send(f.header)
            self.rx = abs(self.rx - 1)

        # ainda precisa implementar ACK not rx
        

    def wait(self, id, f):
        if f.frame_type == DATA:
            self.upperLayer.receive(f.msg)
            f.get_ack_frame(self.rx)
            self.rx = abs(self.rx - 1)
        elif f.frame_type == ACK:
            self.tx = abs(self.tx - 1)
            self.current_state = IDLE

        # ainda precisa implementar TIMEOUT e ACK not tx
