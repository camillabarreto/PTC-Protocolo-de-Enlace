#!/usr/bin/python3

from serial import Serial
import sys
import string


class Communicator:
    def __init__(self, path, rate):
        self.path = path
        self.rate = rate
        try:
            self.serial = Serial(self.path, self.rate)
        except Exception as e:
            print('Não conseguiu acessar a porta serial', e)
            sys.exit(0)

    def transmitter(self, msg):
        msg = msg.encode('ascii')
        n = self.serial.write(msg)
        print(msg)

        print('Enviou %d bytes' % n)
        sys.stdout.flush()

    def receiver(self):
        # recebe até 128 caracteres
        msg = ''
        msg = self.serial.read().decode()
        return msg
