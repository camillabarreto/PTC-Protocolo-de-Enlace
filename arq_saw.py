import poller
from poller import Callback
from sublayer import Sublayer


class ARQ_saw(Sublayer):

    def __init__(self, porta_serial, tout):
        Sublayer.__init__(self, porta_serial, tout)
    
    def send(self, data):
        '''Recebe os octetos da camada superior, trata os dados
        e envia para a camada inferior '''
        self.lowerLayer.send(data)
        

    def receive(self, data):
        '''Recebe os octetos da camada inferior, trata os dados
        e envia para a camada superior '''
        self.upperLayer.receive(data)