#!/usr/bin/python3

from serial import Serial
import sys
import string
import time

class Communicator():
    def __init__(self, path, rate):
        self.path = path 
        self.rate = rate
        
        try:
            self.p = Serial(self.path, self.rate)
        except Exception as e:
            print('Não conseguiu acessar a porta serial', e)
            sys.exit(0)
            
    def transmitter(self, msg):
    	msg = msg.encode('ascii')
    	self.p.write(msg)
    	print('Enviado: ', msg.decode())

    def receiver(self) -> string:
        msg = ''
        while(True):
        	msg += self.p.read().decode()
        	if(msg[len(msg)-1]=='\n'):
        		break;
        		
        print('Recebido: ', msg)
        return msg
    	
if __name__ == '__main__':
	while(True):
		c = Communicator(sys.argv[1], 9600)
		c.transmitter('ameliza ...\r\n')
		c.receiver()
		time.sleep(1)
