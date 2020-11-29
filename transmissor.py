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

msg = 'ameliza elisa camilla ...\r\n'
msg = msg.encode('ascii')

n = p.write(msg)
print(msg)

print('Enviou %d bytes' % n)

print('Digite ENTER para terminar:', end='')
sys.stdout.flush()
sys.stdin.readline()

sys.exit(0)
