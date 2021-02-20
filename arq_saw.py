import poller
from poller import Callback
from sublayer import Sublayer
from frame import Frame
from random import randint

# States
IDLE = 0
WAIT = 1
BACKOFF = 2

# ID
SEND = 0
RECEIVE = 1
TIMEOUT = 2

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
        self.retries = 0
        self.limit_retries = 3
        self.last_frame = Frame() # ultimo quadro enviado é armazenado aqui para casos de retransmissao
        self.switch = {
            IDLE: self.idle,
            WAIT: self.wait,
            BACKOFF: self.backoff
        }


    def handle_timeout(self):
        '''Comunica a FSM que houve timeout, e ela trata o mesmo da forma 
        pertinente ao estado em que se encontra'''
        print("TIMEOUT!")
        self.FSM(TIMEOUT, None)


    def send(self, data):
        '''Recebe os octetos da camada superior, cria um quadro de dados
        com os campos necessários e envia para a camada inferior'''
        self.last_frame.get_data_frame(self.tx, self.id_proto, data)
        self.FSM(SEND, self.last_frame)


    def receive(self, frame):
        '''Comunica a FSM que recebeu um quadro, e ela trata o mesmo da forma 
        pertinente ao estado em que se encontra'''
        self.FSM(RECEIVE, frame)
    
    def FSM(self, id, frame):
        func = self.switch[self.current_state]
        return func(id, frame)


    def idle(self, id, frame):
        # print('IDLE - ARQ')
        if id == SEND and frame.type == DATA:
            # print('ENVIO DATA: ', frame.header)
            self.lowerLayer.send(frame)
            self.current_state = WAIT
            self.reload_timeout()
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
        if id == TIMEOUT:
            self.current_state = BACKOFF
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

        elif id == RECEIVE and frame.type == ACK:
            # print('RECEBE ACK', frame.header)
            if frame.seq == self.tx:
                self.tx = int(not self.tx)
                self.current_state = IDLE
                self.disable_timeout()
            else:
                new_time = randint(1,10) # entre 1s e 10s
                timeout = new_time
                self.current_state = BACKOFF
                
                
    def backoff(self, id, frame):
        # print('BACKOFF - ARQ')
        if id == TIMEOUT:
            if (self.retries == self.limit_retries):
                print("Atingiu o limite de retransmissões")
                self.retries = 0
            else:
                self.lowerLayer.send(self.last_frame)
                self.retries += 1
                self.reload_timeout()
                self.current_state = WAIT
            
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
