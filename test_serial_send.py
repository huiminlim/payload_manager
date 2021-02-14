import serial
import time

ser = serial.Serial('/dev/serial0')
ser.timeout = 10
ser.baudrate = 9600

while True:
	#ser.write(b'hello\r\n')
	print(ser.readline())
