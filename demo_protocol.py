#!/usr/bin/env python3

import poller
import sys
import time
import argparse
from poller import Callback
from serial import Serial
from framing import Framing
from arq_saw import ARQ_saw
from tun import Tun
from tun_interface import Tun_Interface
from application_keyboard import ApplicationKeyboard


if __name__ == '__main__':

    # Visualização de ajuda
    parser = argparse.ArgumentParser(description='Programa de Demonstração')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-s', help='Porta serial utilizada na comunicação', type=str, dest='path', required=True, default="")
    group = requiredNamed.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', action="store", help='IP local e IP remoto', type=str, dest='ip' ,nargs=2, default="")
    group.add_argument('-K', action='store_true', help='Ler do teclado', dest='k', default=False)
    args = parser.parse_args()
    
    # Porta serial
    try: serial = Serial(args.path)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)
    
    # Callbacks
    if not args.k:
        tun = Tun("tun",args.ip[0],args.ip[1],mask="255.255.255.252",mtu=1500,qlen=4)
        tun.start()
        ap = Tun_Interface(tun, 0)
    else: ap = ApplicationKeyboard(sys.stdin, 0)
    fr = Framing(serial, 1)
    saw = ARQ_saw(None, 1)
    ap.connect(None, saw)
    saw.connect(ap, fr)
    fr.connect(saw, None)

    # Poller
    sched = poller.Poller()
    sched.adiciona(ap)
    sched.adiciona(saw)
    sched.adiciona(fr)
    sched.despache()