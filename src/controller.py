import time
import usb.core
import usb.util
from usb.backend import libusb1
from storage import RebtStorage, DEVICE


# You can learn more info from https://github.com/hsutungyu/razer-mouse-battery-windows/blob/main/mamba.pyw
class Rebt:

    def __init__(self) -> None:
        self.needShow = True
        self.config = RebtStorage()
        self.findAll = True
        self.hasDefault = self.config.isExist()
        self.firstRun = not self.hasDefault
        self.backend = libusb1.get_backend(find_library=lambda x: "../libusb-1.0.dll")
        self.mouse = self.get_mouse()

    def map_mouse(self):
        mouses = usb.core.find(find_all=True, idVendor=0x1532, backend=self.backend)
        for mouse in mouses:
            for name, device in DEVICE.items():
                knownProduct = int(device["usbId"], 16)
                if knownProduct == mouse.idProduct:
                    self.config.generate(name, device["usbId"], device["tranId"])
                    self.hasDefault = True
                    return mouse

    def get_mouse(self):
        mouse = None
        if self.hasDefault:
            idProduct = self.config.getDefault("usbId")
            mouse = usb.core.find(idVendor=0x1532, idProduct=idProduct, backend=self.backend)
        if not mouse and self.findAll:
            mouse = self.map_mouse()
        if not mouse:
            raise RuntimeError(f"Mouse cannot be found.")

        return mouse

    def generate_msg(self, transaction_id, command_class, command_id, data_size):
        msgs = [0x00, transaction_id, 0x00, 0x00, 0x00, data_size, command_class, command_id]
        msg = bytes(msgs)
        crc = 0
        for i in msg[2:]:
            crc ^= i
        msg += bytes(80)
        msg += bytes([crc, 0])
        return msg

    def battery_msg(self):
        return self.generate_msg(self.config.getDefault("tranId"), 0x07, 0x80, 0x02)

    def charge_msg(self):
        return self.generate_msg(self.config.getDefault("tranId"), 0x07, 0x84, 0x02)

    def send_msg(self, msg):
        self.mouse = self.get_mouse()
        usb.util.claim_interface(self.mouse, 0)
        self.mouse.set_configuration()
        self.mouse.ctrl_transfer(bmRequestType=0x21,
                                 bRequest=0x09,
                                 wValue=0x300,
                                 data_or_wLength=msg,
                                 wIndex=0x00)
        time.sleep(0.1)
        result = self.mouse.ctrl_transfer(bmRequestType=0xa1,
                                          bRequest=0x01,
                                          wValue=0x300,
                                          data_or_wLength=90,
                                          wIndex=0x00)
        usb.util.dispose_resources(self.mouse)
        usb.util.release_interface(self.mouse, 0)
        return result[9]

    def get_battery(self):
        battery_msg = self.battery_msg()
        battery = self.send_msg(battery_msg)
        if battery == 0: return -1
        return int(battery / 255 * 100)

    def is_charging(self):
        # 1 charging, 0 not
        charge_msg = self.charge_msg()
        return self.send_msg(charge_msg)

    def show_battery_notification(self, battery):
        notification_battery = self.config.getDefault("notification")
        if notification_battery == 0:
            return False

        if battery > notification_battery:
            self.needShow = True
            return False

        if self.needShow:
            self.needShow = False
            return True
