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
print(p.read(14))

msg = p.read(128)
print('Recebeu: ', msg)

sys.exit(0)
