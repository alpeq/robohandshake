import bluetooth
bt_add_sensor = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
port = 3
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bt_add_sensor,port))
print(bluetooth.discover_devices())
print("Connected")
while True:
    try:
        data = input()
        sock.send(data.encode())
        if data == 'CLOSE':
            break
    except KeyboardInterrupt:
        sock.close()
