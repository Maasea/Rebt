import time
import usb.core
import usb.util
from usb.backend import libusb1
from storage import RazerStorage,DEVICE

class Razer():

    def __init__(self) -> None:
        self.config = RazerStorage()
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
                    self.config.generate(name, device["usbId"],device["tranId"])
                    self.hasDefault=True
                    return mouse

    def get_mouse(self):
        """
        Function that checks whether the mouse is plugged in or not
        :return: [mouse, wireless]: a list that stores (1) a Device object that represents the mouse; and
        (2) a boolean for stating if the mouse is in wireless state (True) or wired state (False)
        """
        mouse = None
        if self.hasDefault:
            idProduct = self.config.getDefault("usbId")
            mouse = usb.core.find(idVendor=0x1532,
                                  idProduct=idProduct,
                                  backend=self.backend)
        if not mouse and self.findAll:
            mouse = self.map_mouse()

        # if the receiver is not found, mouse would be None

        # still not found, then the mouse is not plugged in, raise error
        if not mouse:
            raise RuntimeError(f"Mouse cannot be found.")

        return mouse

    def battery_msg(self):
        """
        Function that creates and returns the message to be sent to the device
        :return: meg: the message to be sent to the mouse for getting the battery level
        """
        # adapted from https://github.com/rsmith-nl/scripts/blob/main/set-ornata-chroma-rgb.py
        # the first 8 bytes in order from left to right
        # status + transaction_id.id + remaining packets (\x00\x00) + protocol_type + command_class + command_id + data_size
        msg = b"\x00" + self.config.getDefault("tranId") + b"\x00\x00\x00\x02\x07\x80"
        crc = 0
        for i in msg[2:]:
            crc ^= i
        # the next 80 bytes would be storing the data to be sent, but for getting the battery no data is sent
        msg += bytes(80)
        # the last 2 bytes would be the crc and a zero byte
        msg += bytes([crc, 0])
        return msg

    def get_battery(self):
        """
        Function for getting the battery level of a Razer Mamba Wireless, or other device if adapted
        :return: a string with the battery level as a percentage (0 - 100)
        """
        # find the mouse and the state, see get_mouse() for detail
        # the message to be sent to the mouse, see battery_msg() for detail
        # logging.info(f"Message sent to the mouse: {list(msg)}")
        # needed by PyUSB
        # if Linux, need to detach kernel driver
        self.mouse = self.get_mouse()
        self.mouse.set_configuration()
        usb.util.claim_interface(self.mouse, 0)
        # send request (battery), see razer_send_control_msg in razercommon.c in OpenRazer driver for detail
        self.mouse.ctrl_transfer(bmRequestType=0x21,
                                 bRequest=0x09,
                                 wValue=0x300,
                                 data_or_wLength=self.battery_msg(),
                                 wIndex=0x00)
        # needed by PyUSB
        usb.util.dispose_resources(self.mouse)
        # if the mouse is wireless, need to wait before getting response
        time.sleep(0.3305)
        # receive response
        result = self.mouse.ctrl_transfer(bmRequestType=0xa1,
                                          bRequest=0x01,
                                          wValue=0x300,
                                          data_or_wLength=90,
                                          wIndex=0x00)
        usb.util.dispose_resources(self.mouse)
        usb.util.release_interface(self.mouse, 0)
        # logging.info(f"Message received from the mouse: {list(result)}")
        # the raw battery level is in 0 - 255, scale it to 100 for human, correct to 2 decimal places
        return int(result[9] / 255 * 100)