#!/usr/bin/env python3

import poller
import sys
import time
import argparse
from poller import Callback
from serial import Serial
from application import Application
from application_keyboard import ApplicationKeyboard
from framing import Framing
from arq_saw import ARQ_saw


if __name__ == '__main__':

    # Visualização de ajuda
    parser = argparse.ArgumentParser(description='Programa de Demonstração')
    parser.add_argument('-s', '--serialPath', help='Porta serial onde ocorrerá a comunicação', type=str,
                        dest='path', required=False, default="")
    parser.add_argument('-f', '--fakeFile', help='Arquivo com o conteúdo que será transmitido', type=str,
                        dest='file', required=False, default="")
    parser.add_argument('-r', '--rate', help='Taxa de transmissão da porta serial', type=str,
                        dest='rate', required=False, default="")
    args = parser.parse_args()
    
    # Porta serial
    try:
        serial = Serial(args.path, args.rate)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

	# # File
    # try:
    #     arq = open(args.file, 'rb')
    # except Exception as e:
    #     print('Não conseguiu acessar arquivo', e)
    #     sys.exit(0)

    arq = sys.stdin  # para testes
    
    # Callbacks

    ap = ApplicationKeyboard(arq, 0) # para testes
    # ap = Application(arq, 0)
    fr = Framing(serial, 1)
    saw = ARQ_saw(None, 2)
    ap.connect(None, saw)
    saw.connect(ap, fr)
    fr.connect(saw, None)

    # Poller
    sched = poller.Poller()
    sched.adiciona(ap)
    sched.adiciona(saw)
    sched.adiciona(fr)
    sched.despache()