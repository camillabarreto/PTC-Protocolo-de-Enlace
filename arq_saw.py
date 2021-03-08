import poller
from poller import Callback
from sublayer import Sublayer
from frame import Frame
from random import randint

# States
IDLE = 0
WAIT = 1
BACKOFF = 2
ON_HOLD = 3

# ID
SEND = 0
RECEIVE = 1
TIMEOUT = 2

# FRAME TYPES
DATA = 0
ACK = 1

# PROTOCOLS
IPV4 = 0x800
IPV6 = 0x86dd

# Letter Colors
RED = '\033[31m'
YELLOW = '\033[33m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RST = '\033[0;0m'

'''A subcamada ARQ_saw é resposável por garantir a entrega das 
transmissões através da combinação do mecanismo Stop and Wait e ALOHA. 
Na transmissão (def send) os octetos são encapsulados formando um frame com os campos de: 
        CONTROLE(1B), RESERVADO(1B), IDPROTO(1B), DADOS(<=1024B), FCS(2B).
As transmissões são seguidas da espera pelo frame de confirmação (ACK).
Enquanto não houver confirmação o frame será retransmitido periodicamente.
Na recepção (def receive) de frame de dados a mensagem será desencapsulada e 
entregue a camada superior se corresponder ao número de sequência esperado. Para todos 
os frames de dados recebidos são enviados ACK com o número de sequência correspondente.
São definidos timers de contenção (def handle_timeout) para confirmação de frame, para retransmissões
de frames não confirmados e para novas transmissões.'''


class ARQ_saw(Sublayer):
    def __init__(self, porta_serial, tout):
        Sublayer.__init__(self, porta_serial, tout)
        self.disable_timeout()
        self.current_state = IDLE
        self.rx = 0
        self.tx = 0
        self.slot_time = 0.1
        self.slot_min = 0
        self.slot_max = 7
        self.last_frame = Frame() # armazenado para casos de retransmissao
        self.switch = {
            IDLE: self.idle,
            WAIT: self.wait,
            BACKOFF: self.backoff,
            ON_HOLD: self.on_hold
        }

    def handle_timeout(self):
        '''Sinaliza TIMEOUT para a FSM fazer o tratamento 
        pertinente ao estado em que se encontra'''
        self.FSM(TIMEOUT, None)

    def send(self, data, proto):
        '''Recebe octetos da camada superior, cria um frame de dados
        e sinaliza SEND para a FSM fazer o tratamento pertinente ao estado em que se encontra'''
        if proto == IPV4: proto = 1
        else: proto = 2
        self.last_frame.get_data_frame(self.tx, proto, data)
        self.FSM(SEND, self.last_frame)

    def receive(self, frame):
        '''Recebe frame da camada inferior e sinaliza RECEIVE para a FSM fazer o tratamento 
        pertinente ao estado em que se encontra'''
        self.FSM(RECEIVE, frame)
    
    ###### FINITE STATE MACHINE

    def FSM(self, id, frame):
        func = self.switch[self.current_state]
        return func(id, frame)

    def idle(self, id, frame):
        if id == SEND and frame.type == DATA:
            self.lowerLayer.send(frame)
            self.reload_timeout()
            self.enable_timeout()
            self.current_state = WAIT

        elif id == RECEIVE and frame.type == DATA:
            self._receive_data(frame)

    def wait(self, id, frame):
        if id == TIMEOUT:
            print(YELLOW+"TIMEOUT!"+RST+" Retransmitindo...")
            new_time = self.slot_time*randint(self.slot_min,self.slot_max)
            self.timeout = new_time
            self.current_state = BACKOFF

        elif id == RECEIVE and frame.type == DATA:
            self._receive_data(frame)
        
        elif id == RECEIVE and frame.type == ACK:
            if frame.seq == self.tx:
                self.tx = int(not self.tx)
                self.current_state = ON_HOLD
        
            else: self.current_state = BACKOFF
        
            new_time = self.slot_time*randint(self.slot_min,self.slot_max)
            self.timeout = new_time
                
    def backoff(self, id, frame):
        if id == TIMEOUT:
            self.lowerLayer.send(self.last_frame)
            self.reload_timeout()
            self.current_state = WAIT
        
        elif id == RECEIVE and frame.type == DATA:
            self._receive_data(frame)
            
    def on_hold(self, id, frame):
        if id == TIMEOUT:
            self.current_state = IDLE
            self.disable_timeout()
        
        elif id == RECEIVE and frame.type == DATA:
            self._receive_data(frame)
    
    def _receive_data(self, frame):
        if frame.seq == self.rx:
            if frame.id_proto == 1: self.upperLayer.receive(frame.msg, IPV4)
            else: self.upperLayer.receive(frame.msg, IPV6)
            self.rx = int(not self.rx)
        
        frame.get_ack_frame(frame.seq)
        self.lowerLayer.send(frame)