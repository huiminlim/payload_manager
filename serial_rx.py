import serial

ser = serial.Serial('/dev/serial0', 9600)
ser.flush()

while True:
    try:
        line = ser.readline()
        print(line.decode("utf-8").replace("\r\n", ""))
    except KeyboardInterrupt:
        print("Close")
        ser.close()
