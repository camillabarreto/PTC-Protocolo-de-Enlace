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
        self.id_proto = 4
        self.last_frame = Frame() # ultimo quadro enviado é armazenado aqui para casos de retransmissao


    def handle_timeout(self):
        '''Adicionar descrição '''
        print("TIMEOUT!")
        self.lowerLayer.send(self.last_frame)
        self.reload_timeout()
        # acho que nao ta funcionando pq essa subcamada tem fileobj = None
        # pra testar tem que comentar os envios de frames DATA para a camada inferior


    def send(self, data):
        '''Adicionar descrição '''
        self.last_frame.get_data_frame(self.tx, self.id_proto, data)
        self.FSM(SEND, self.last_frame)


    def receive(self, frame):
        '''Adicionar descrição '''
        self.FSM(RECEIVE, frame)
    
    def FSM(self, id, frame):
        switch = {
            IDLE: self.idle,
            WAIT: self.wait
        }
        func = switch.get(self.current_state, lambda: None)
        return func(id, frame)


    def idle(self, id, frame):
        # print('IDLE - ARQ')
        if id == SEND and frame.type == DATA:
            # print('ENVIO DATA: ', frame.header)
            self.lowerLayer.send(frame)
            self.current_state = WAIT
            self.enable_timeout()

        elif id == RECEIVE and frame.type == DATA:
            # print('RECEBE DATA', frame.header)
            if frame.seq == self.rx:
                self.upperLayer.receive(frame.msg)
                frame.get_ack_frame(self.rx)
                self.rx = int(not self.rx)
            else:
                frame.get_ack_frame(frame.seq)
            # print('ENVIO ACK', frame.header)
            self.lowerLayer.send(frame)

    def wait(self, id, frame):
        # print('WAIT - ARQ')
        if id == RECEIVE and frame.type == DATA:
            # print('RECEBE DATA', frame.header)
            if frame.seq == self.rx:
                self.upperLayer.receive(frame.msg)
                frame.get_ack_frame(self.rx)
                self.rx = int(not self.rx)
            else:
                frame.get_ack_frame(frame.seq)
            # print('ENVIO ACK', frame.header)
            self.lowerLayer.send(frame)

        elif id == RECEIVE and frame.type == ACK:
            # print('RECEBE ACK', frame.header)
            if frame.seq == self.tx:
                self.tx = int(not self.tx)
                self.current_state = IDLE
                self.disable_timeout()
            else:
                self.lowerLayer.send(self.last_frame)
