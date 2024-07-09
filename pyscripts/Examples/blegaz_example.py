import BLE_GATT
import struct
#from gi.repository import GLib

ubit_address = "28:CD:C1:01:D5:21"
uart_rx = ""
uart_tx = ""

import bluetooth
bt_uuid = "00002A6E-0000-1000-8000-00805F9B34FB"
#Writing those long numbers is cumbersome so Bluetooth official characteristics can be shortened to 16-bits. This means you will often see the above Device Name Characteristic written as 0x2A00 although on the system it will still be the 128-bit value. The official Bluetooth base UUID is: 0000xxxx-0000-1000-8000-00805F9B34FB and the 16-bit value replaces the x's.
def notify_handler(value):
    print(f"Received: {bytes(value).decode('UTF-8')}")

def send_ping():
    print('sending: ping')
    ubit.char_write(uart_rx, b'ping\n')
    return True


ubit = BLE_GATT.Central(ubit_address)
ubit.connect()

def my_callback(value):
    print(value)
    #print(struct.unpack("<h", value)[0] / 100)
    print(struct.unpack("<h",[bytes(stuff, 'utf-8') for stuff in value])[0] / 100)

ubit.on_value_change(bt_uuid, my_callback)
#GLib.timeout_add_seconds(20, send_ping)
ubit.wait_for_notifications()

#help(my_device.adapter)
#help(my_device.device)
#help(my_device.chrcs[my_custom_uuid.casefold()])

