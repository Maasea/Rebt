import time
import usb.core
import usb.util
from usb.backend import libusb1
from storage import RebtStorage, DEVICE


# You can learn more info from https://github.com/hsutungyu/razer-mouse-battery-windows/blob/main/mamba.pyw
class Rebt:

    def __init__(self) -> None:
        self.config = RebtStorage()
        self.findAll = True
        self.hasDefault = self.config.isExist()
        self.firstRun = not self.hasDefault
        self.backend = libusb1.get_backend()
        self.mouse = self.get_mouse()

    def map_mouse(self):
        mouses = usb.core.find(find_all=True,
                               idVendor=0x1532,
                               backend=self.backend)
        for mouse in mouses:
            for name, device in DEVICE.items():
                knowProduct = int(device["usbId"], 16)
                if knowProduct == mouse.idProduct:
                    self.config.generate(name, device["usbId"],
                                         device["tranId"])
                    self.hasDefault = True
                    return mouse

    def get_mouse(self):
        mouse = None
        if self.hasDefault:
            idProduct = self.config.getDefault("usbId")
            mouse = usb.core.find(idVendor=0x1532,
                                  idProduct=idProduct,
                                  backend=self.backend)
        if not mouse and self.findAll:
            mouse = self.map_mouse()
        if not mouse:
            raise RuntimeError(f"Mouse cannot be found.")

        return mouse

    def battery_msg(self):
        msg = b"\x00" + self.config.getDefault("tranId") + b"\x00\x00\x00\x02\x07\x80"
        crc = 0
        for i in msg[2:]:
            crc ^= i
        msg += bytes(80)
        msg += bytes([crc, 0])
        return msg

    def get_battery(self):
        self.mouse = self.get_mouse()
        usb.util.claim_interface(self.mouse, 0)
        self.mouse.set_configuration()
        self.mouse.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x300, data_or_wLength=self.battery_msg(),
                                 wIndex=0x00)
        time.sleep(0.1)
        result = self.mouse.ctrl_transfer(bmRequestType=0xa1,
                                          bRequest=0x01,
                                          wValue=0x300,
                                          data_or_wLength=90,
                                          wIndex=0x00)
        usb.util.dispose_resources(self.mouse)
        usb.util.release_interface(self.mouse, 0)
        return int(result[9] / 255 * 100)
