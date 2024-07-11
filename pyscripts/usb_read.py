import serial

ser = serial.Serial("/dev/ttyACM1")
while True:
  line = ser.readline()
  the_dict = eval(line.decode().strip())
  print(line)
  print(the_dict['palm'])
  print("******")
