from configparser import ConfigParser
from pathlib import Path
import os

DEVICE = {
    "RAZER_OROCHI_2011": {
        "usbId": "0x0013",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_3_5G": {
        "usbId": "0x0016",
        "tranId": "0xff"
    },
    "RAZER_ABYSSUS_1800": {
        "usbId": "0x0020",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_2012_WIRED": {
        "usbId": "0x0024",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_2012_WIRELESS": {
        "usbId": "0x0025",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_3_5G_BLACK": {
        "usbId": "0x0029",
        "tranId": "0xff"
    },
    "RAZER_NAGA_2012": {
        "usbId": "0x002E",
        "tranId": "0xff"
    },
    "RAZER_IMPERATOR": {
        "usbId": "0x002F",
        "tranId": "0xff"
    },
    "RAZER_OUROBOROS": {
        "usbId": "0x0032",
        "tranId": "0xff"
    },
    "RAZER_TAIPAN": {
        "usbId": "0x0034",
        "tranId": "0xff"
    },
    "RAZER_NAGA_HEX_RED": {
        "usbId": "0x0036",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_2013": {
        "usbId": "0x0037",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_1800": {
        "usbId": "0x0038",
        "tranId": "0xff"
    },
    "RAZER_OROCHI_2013": {
        "usbId": "0x0039",
        "tranId": "0xff"
    },
    "RAZER_NAGA_EPIC_CHROMA": {
        "usbId": "0x003E",
        "tranId": "0xff"
    },
    "RAZER_NAGA_EPIC_CHROMA_DOCK": {
        "usbId": "0x003F",
        "tranId": "0xff"
    },
    "RAZER_NAGA_2014": {
        "usbId": "0x0040",
        "tranId": "0xff"
    },
    "RAZER_NAGA_HEX": {
        "usbId": "0x0041",
        "tranId": "0xff"
    },
    "RAZER_ABYSSUS": {
        "usbId": "0x0042",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_CHROMA": {
        "usbId": "0x0043",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_WIRED": {
        "usbId": "0x0044",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_WIRELESS": {
        "usbId": "0x0045",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_TE_WIRED": {
        "usbId": "0x0046",
        "tranId": "0xff"
    },
    "RAZER_OROCHI_CHROMA": {
        "usbId": "0x0048",
        "tranId": "0xff"
    },
    "RAZER_DIAMONDBACK_CHROMA": {
        "usbId": "0x004C",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_2000": {
        "usbId": "0x004F",
        "tranId": "0xff"
    },
    "RAZER_NAGA_HEX_V2": {
        "usbId": "0x0050",
        "tranId": "0xff"
    },
    "RAZER_NAGA_CHROMA": {
        "usbId": "0x0053",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_3500": {
        "usbId": "0x0054",
        "tranId": "0xff"
    },
    "RAZER_LANCEHEAD_WIRED": {
        "usbId": "0x0059",
        "tranId": "0x3f"
    },
    "RAZER_LANCEHEAD_WIRELESS": {
        "usbId": "0x005A",
        "tranId": "0x3f"
    },
    "RAZER_ABYSSUS_V2": {
        "usbId": "0x005B",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_ELITE": {
        "usbId": "0x005C",
        "tranId": "0xff"
    },
    "RAZER_ABYSSUS_2000": {
        "usbId": "0x005E",
        "tranId": "0xff"
    },
    "RAZER_LANCEHEAD_TE_WIRED": {
        "usbId": "0x0060",
        "tranId": "0xff"
    },
    "RAZER_ATHERIS_RECEIVER": {
        "usbId": "0x0062",
        "tranId": "0x1f"
    },
    "RAZER_BASILISK": {
        "usbId": "0x0064",
        "tranId": "0xff"
    },
    "RAZER_BASILISK_ESSENTIAL": {
        "usbId": "0x0065",
        "tranId": "0xff"
    },
    "RAZER_NAGA_TRINITY": {
        "usbId": "0x0067",
        "tranId": "0xff"
    },
    "RAZER_ABYSSUS_ELITE_DVA_EDITION": {
        "usbId": "0x006A",
        "tranId": "0xff"
    },
    "RAZER_ABYSSUS_ESSENTIAL": {
        "usbId": "0x006B",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_ELITE": {
        "usbId": "0x006C",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_ESSENTIAL": {
        "usbId": "0x006E",
        "tranId": "0xff"
    },
    "RAZER_LANCEHEAD_WIRELESS_RECEIVER": {
        "usbId": "0x006F",
        "tranId": "0x1f"
    },
    "RAZER_LANCEHEAD_WIRELESS_WIRED": {
        "usbId": "0x0070",
        "tranId": "0x1f"
    },
    "RAZER_DEATHADDER_ESSENTIAL_WHITE_EDITION": {
        "usbId": "0x0071",
        "tranId": "0xff"
    },
    "RAZER_MAMBA_WIRELESS_RECEIVER": {
        "usbId": "0x0072",
        "tranId": "0x3f"
    },
    "RAZER_MAMBA_WIRELESS_WIRED": {
        "usbId": "0x0073",
        "tranId": "0x3f"
    },
    "RAZER_PRO_CLICK_RECEIVER": {
        "usbId": "0x0077",
        "tranId": "0x1f"
    },
    "RAZER_VIPER": {
        "usbId": "0x0078",
        "tranId": "0xff"
    },
    "RAZER_VIPER_ULTIMATE_WIRED": {
        "usbId": "0x007A",
        "tranId": "0xff"
    },
    "RAZER_VIPER_ULTIMATE_WIRELESS": {
        "usbId": "0x007B",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_V2_PRO_WIRED": {
        "usbId": "0x007C",
        "tranId": "0x3f"
    },
    "RAZER_DEATHADDER_V2_PRO_WIRELESS": {
        "usbId": "0x007D",
        "tranId": "0x3f"
    },
    "RAZER_PRO_CLICK_WIRED": {
        "usbId": "0x0080",
        "tranId": "0x1f"
    },
    "RAZER_BASILISK_X_HYPERSPEED": {
        "usbId": "0x0083",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_V2": {
        "usbId": "0x0084",
        "tranId": "0xff"
    },
    "RAZER_BASILISK_V2": {
        "usbId": "0x0085",
        "tranId": "0xff"
    },
    "RAZER_BASILISK_ULTIMATE_WIRED": {
        "usbId": "0x0086",
        "tranId": "0x1f"
    },
    "RAZER_BASILISK_ULTIMATE_RECEIVER": {
        "usbId": "0x0088",
        "tranId": "0x1f"
    },
    "RAZER_VIPER_MINI": {
        "usbId": "0x008A",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_V2_MINI": {
        "usbId": "0x008C",
        "tranId": "0xff"
    },
    "RAZER_NAGA_LEFT_HANDED_2020": {
        "usbId": "0x008D",
        "tranId": "0xff"
    },
    "RAZER_NAGA_PRO_WIRED": {
        "usbId": "0x008F",
        "tranId": "0x1f"
    },
    "RAZER_NAGA_PRO_WIRELESS": {
        "usbId": "0x0090",
        "tranId": "0x1f"
    },
    "RAZER_VIPER_8K": {
        "usbId": "0x0091",
        "tranId": "0xff"
    },
    "RAZER_OROCHI_V2_RECEIVER": {
        "usbId": "0x0094",
        "tranId": "0x1f"
    },
    "RAZER_OROCHI_V2_BLUETOOTH": {
        "usbId": "0x0095",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_ESSENTIAL_2021": {
        "usbId": "0x0098",
        "tranId": "0xff"
    },
    "RAZER_BASILISK_V3": {
        "usbId": "0x0099",
        "tranId": "0xff"
    },
    "RAZER_DEATHADDER_V2_X_HYPERSPEED": {
        "usbId": "0x009C",
        "tranId": "0x1f"
    },
    "RAZER_VIPER_V2_PRO_WIRED": {
        "usbId": "0x00A5",
        "tranId": "0x1f"
    },
    "RAZER_VIPER_V2_PRO_WIRELESS": {
        "usbId": "0x00A6",
        "tranId": "0x1f"
    }
}


class RebtStorage:

    def __init__(self):
        self.config = ConfigParser()
        self.filename = "rebt.ini"
        self.path = os.path.join(Path.home(), self.filename)
        self.config["DEFAULT"] = {}
        self.setInterval(15)
        self.setTrayStyle(0)
        self.setScale("seconds")
        self.setNotification(15)
        self.readConfig()

    def isExist(self):
        return os.path.exists(self.path)

    def readConfig(self):
        if self.isExist():
            self.config.read(self.path)

    def generate(self, devcieName, usbId, tranId):
        self.setDevice(devcieName, usbId, tranId)
        self.save()

    def getDefault(self, option):
        value = self.config.get("DEFAULT", option)
        if option == "interval": value = int(value)
        if option == "usbId": value = int(value, 16)
        if option == "tranId": value = int(value, 16)
        if option == "trayStyle": value = int(value)
        if option == "notification": value = int(value)
        return value

    def setInterval(self, interval):
        self.config.set("DEFAULT", "interval", str(interval))

    def setDevice(self, devcieName, usbId, tranId):
        self.config.set("DEFAULT", "name", devcieName)
        self.config.set("DEFAULT", "usbId", usbId)
        self.config.set("DEFAULT", "tranId", tranId)

    def setTrayStyle(self, style):
        self.config.set("DEFAULT", "trayStyle", str(style))

    def setScale(self, scale):
        self.config.set("DEFAULT", "scale", scale)

    def setNotification(self, battery):
        self.config.set("DEFAULT", "notification", str(battery))

    def save(self):
        with open(self.path, "w") as configfile:
            self.config.write(configfile)
