import poller
from poller import Callback
from sublayer import Sublayer
from header import Header


class ARQ_saw(Sublayer):

    def __init__(self, porta_serial, tout):
        Sublayer.__init__(self, porta_serial, tout)
        self.count = 0;
        self.id_proto = 0x80 # ipv4
    
    def send(self, data):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a camada inferior '''
        self.count += 1
        tx = Header()
        header = tx.get_data_frame(self.count, self.id_proto, data)
        print(header)
        self.lowerLayer.send(data)
        

    def receive(self, data):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para a camada superior '''
        rx = Header()
        rx.detach_frame(data)
        print(self.msg)
        self.upperLayer.receive(data)
