#!/usr/bin/python3

from Communicator import Communicator
import sys
import time
import asyncio

path = sys.argv[1]
try:
    c = Communicator(path, 9600)
except Exception as e:
    print('Não conseguiu acessar a porta serial', e)
    sys.exit(0)

i = 0
while(True):
    msg = 'ameliza elisa camilla ...\r\n'
    c.transmitter(msg)
    msg = ''
    while(True):
        msg += c.receiver()
        if(msg[len(msg)-1] == '\n'):
            break
    print('final msg: ', msg.encode('ascii'), ' ', i)
    i = i+1
    time.sleep(1)

sys.exit(0)
