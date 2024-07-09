import gatt

from argparse import ArgumentParser


class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        service = self.services[0]
        print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
        charact = service.characteristics[0]
        charact.read_value()

    def characteristic_value_updated(self, characteristic, value):
        print("value:", value.decode('windows-1252'))
        #print("value:", value.decode("utf-8"))
        #print("Firmware version:", value.decode("utf-8"))


#arg_parser = ArgumentParser(description="GATT Connect Demo")
#arg_parser.add_argument('mac_address', help="MAC address of device to connect")
#args = arg_parser.parse_args()

print("Connecting...")

manager = gatt.DeviceManager(adapter_name='hci0')

device = AnyDevice(manager=manager, mac_address='28:CD:C1:01:D5:21')
device.connect()

manager.run()