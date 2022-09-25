import sys
import time
import resource
from storage import DEVICE
from controller import Razer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QToolTip
from PySide2.QtCore import Qt, QRectF, QTimer, QObject, Signal, QFile
from PySide2.QtGui import QIcon, QPainterPath, QRegion, QTransform, QCursor
from threading import Thread


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Razer battery Properties
        self.full = QIcon(':/resource/imgs/full.svg')
        self.most = QIcon(':/resource/imgs/most.svg')
        self.half = QIcon(':/resource/imgs/half.svg')
        self.low = QIcon(':/resource/imgs/low.svg')
        self.empty = QIcon(':/resource/imgs/empty.svg')
        self.defaultIcon = QIcon(':/resource/imgs/icon.ico')
        self.curIcon = self.defaultIcon
        self.clickCount = 0

        # Init System tray
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.curIcon)
        self.tray.activated.connect(self.trigger)
        self.tray.setVisible(True)
        try:
            self.rz = Razer()
            self.minutes = self.rz.config.getDefault(
                "interval")  # refresh interval
        except RuntimeError as e:
            self.tray.showMessage("Error", str(e), self.curIcon)
            time.sleep(4)
            sys.exit(0)

        if self.rz.firstRun:
            self.tray.showMessage(
                "Detected",
                self.rz.config.getDefault("name").replace("_", " "),
                self.curIcon)
        # Popup window Properties
        self.window_width = 400
        self.window_height = 260
        self.setFixedSize(self.window_width, self.window_height)
        self.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)

        # Init Control Pannel
        uiFile = QFile(':/resource/tool.ui')
        uiFile.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.controlPanel = loader.load(uiFile, self)
        uiFile.close()
        self.controlPanel.setFixedSize(self.window_width, self.window_height)
        self.controlPanel.closeButton.clicked.connect(app.quit)
        self.controlPanel.intervalSlider.setValue(self.minutes)
        self.controlPanel.intervalLabel.setText(str(self.minutes))
        self.controlPanel.intervalSlider.sliderMoved.connect(
            lambda value: QToolTip.showText(QCursor.pos(), str(value)))
        self.controlPanel.intervalSlider.sliderReleased.connect(
            self.updateInterval)
        self.controlPanel.deviceBox.addItems(DEVICE.keys())
        self.controlPanel.deviceBox.setCurrentText(
            self.rz.config.getDefault("name"))
        self.controlPanel.deviceBox.currentTextChanged.connect(
            self.updateDevice)
        self.setCentralWidget(self.controlPanel)

        # backgroundRefresh when show window
        self.refreshSignal = RefreshSignal()
        self.refreshSignal.update.connect(self.backRefresh)
        # update
        self.refreshSignal.update.emit()

        # Popup window show position
        self.changeShowPosition()

        self.radius = 18
        self.setStyleSheet('''
            QMenu {{
                border-radius: {radius}px;
            }}
        '''.format(radius=self.radius))

        # Init razer battery refresh Timer
        self.timer = QTimer()
        self.timer.setInterval(self.minutes * 60 * 1000)
        self.timer.timeout.connect(self.updateBatteryInfo)
        self.timer.start()

    def hideEvent(self, event):
        # tray position
        tPosition = self.tray.geometry()
        min_x = tPosition.x()
        max_x = min_x + tPosition.width()
        min_y = tPosition.y()
        max_y = min_y + tPosition.height()

        # cursor position
        cPosition = QCursor.pos()
        c_x = cPosition.x()
        c_y = cPosition.y()

        if not (min_x < c_x and c_x < max_x and min_y < c_y and c_y < max_y):
            self.clickCount += 1
        return super().hideEvent(event)

    def resizeEvent(self, event):
        # https://stackoverflow.com/questions/65574567/rounded-corners-for-qmenu-in-pyqt
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region)

    def trigger(self, reason):
        if reason == QSystemTrayIcon.MiddleClick:
            app.quit()
        elif reason == QSystemTrayIcon.Trigger:
            self.clickCount += 1
            if self.clickCount % 2:
                self.changeShowPosition()
                self.show()
                self.refreshSignal.update.emit()

    def changeShowPosition(self):
        trayPosition = self.tray.geometry()
        x = trayPosition.x() - (
            (self.window_width - trayPosition.width()) >> 1)
        y = trayPosition.y() - (self.window_height + 20)
        self.move(x, y)

    def getBatteryInfo(self):
        try:
            battery = self.rz.get_battery()
        except RuntimeError as e:
            battery = 0
            self.tray.showMessage("Error", str(e), self.defaultIcon)
        icon = self.full
        if battery <= 85:
            icon = self.most
        if battery <= 65:
            icon = self.half
        if battery <= 35:
            icon = self.low
        if battery <= 10:
            icon = self.empty
        return icon, battery

    def updateBatteryInfo(self):
        icon, battery = self.getBatteryInfo()
        self.tray.setToolTip(f"{battery}%")
        self.controlPanel.battery.setText(f' {battery}%')
        if icon != self.curIcon:
            self.tray.setIcon(icon)
            self.controlPanel.battery.setIcon(icon)
            self.curIcon = icon

    def updateInterval(self):
        minutes = self.controlPanel.intervalSlider.value()
        self.controlPanel.intervalLabel.setText(str(minutes))
        self.timer.setInterval(minutes * 60 * 1000)

        # write to default file
        self.rz.config.setInterval(minutes)
        self.rz.config.save()

    def updateDevice(self, name):
        deviceInfo = DEVICE[name]
        self.rz.config.setDevice(name, deviceInfo["usbId"],
                                 deviceInfo["tranId"])
        self.rz.findAll = False
        self.refreshSignal.update.emit()
        self.rz.config.save()

    def backRefresh(self):
        t = Thread(target=self.updateBatteryInfo)
        t.start()


class RefreshSignal(QObject):
    update = Signal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())