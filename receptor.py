#!/usr/bin/python3

from serial import Serial
import sys

try:
  porta = sys.argv[1]
except:
  print('Uso: %s porta_serial' % sys.argv[0])
  sys.exit(0)

try:
  p = Serial(porta, 9600)
except Exception as e:
  print('Não conseguiu acessar a porta serial', e)
  sys.exit(0)

# recebe até 128 caracteres
n = 0
msg = ''

while(True):
	msg += p.read().decode()
	if(msg[len(msg)-1]=='\n'):
		break;
	

print('final msg: ', msg.encode('ascii'))
#if(msg(len(msg)).decode()=='\n'):
		
sys.exit(0)
