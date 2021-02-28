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


if __name__ == '__main__':

    # Visualização de ajuda
    parser = argparse.ArgumentParser(description='Programa de Demonstração')
    parser.add_argument('-s', help='Porta serial utilizada na comunicação', type=str,
                        dest='path', required=False, default="")
    parser.add_argument('-r', help='Taxa de transmissão da porta serial', type=str,
                        dest='rate', required=False, default="")
    parser.add_argument('-t', help='IP origem e IP destino', type=str, 
                        dest='ip', nargs='+', required=False, default="")
    args = parser.parse_args()
    
    # Porta serial
    try:
        serial = Serial(args.path, args.rate)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    # Tun
    tun = Tun("tun",args.ip[0],args.ip[1],mask="255.255.255.252",mtu=1500,qlen=4)
    tun.start()
    
    # Callbacks
    tun_int = Tun_Interface(tun, 0)
    fr = Framing(serial, 1)
    saw = ARQ_saw(None, 1)
    tun_int.connect(None, saw)
    saw.connect(tun_int, fr)
    fr.connect(saw, None)

    # Poller
    sched = poller.Poller()
    sched.adiciona(tun_int)
    sched.adiciona(saw)
    sched.adiciona(fr)
    sched.despache()