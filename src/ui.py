import sys
import time
import resource
from drawtray import TrayIcon, IconStyle
from storage import DEVICE
from controller import Rebt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QToolTip
from PySide2.QtCore import Qt, QRectF, QTimer, QObject, Signal, QThread
from PySide2.QtGui import QIcon, QPainterPath, QRegion, QTransform, QCursor, QPixmap, QPainter, QFont
from darkdetect import DarkMode


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Icon
        self.defaultIcon = QIcon(":/resource/imgs/icon.png")
        self.setWindowIcon(self.defaultIcon)
        self.clickCount = 0
        self.curBattery = -1
        self.chargeStatus = 0

        # Init System tray
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.defaultIcon)
        self.tray.activated.connect(self.trigger)
        self.tray.setVisible(True)
        try:
            self.rebt = Rebt()
            self.interval = self.rebt.config.getDefault("interval")
            self.scale = self.rebt.config.getDefault("scale")
        except RuntimeError as e:
            print(e)
            self.tray.showMessage("Error", str(e), self.defaultIcon)
            time.sleep(4)
            sys.exit(0)
        if self.rebt.firstRun:
            self.tray.showMessage("Detected",
                                  self.rebt.config.getDefault("name").replace("_", " "),
                                  self.defaultIcon)

        # Popup window Properties
        self.window_width = 400
        self.window_height = 260
        self.setFixedSize(self.window_width, self.window_height)
        self.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)
        # Init Control Panel
        self.controlPanel = QUiLoader().load(":/resource/tool.ui")
        self.controlPanel.setFixedSize(self.window_width, self.window_height)
        self.controlPanel.closeButton.clicked.connect(self.quitApp)
        self.controlPanel.intervalSlider.setValue(self.interval)
        self.controlPanel.intervalLabel.setText(str(self.interval))
        self.controlPanel.intervalSlider.sliderMoved.connect(self.showTips)
        self.controlPanel.intervalSlider.sliderReleased.connect(self.updateInterval)
        self.controlPanel.deviceBox.addItems(DEVICE.keys())
        self.controlPanel.deviceBox.setCurrentText(self.rebt.config.getDefault("name"))
        self.controlPanel.deviceBox.currentTextChanged.connect(self.updateDevice)
        self.setCentralWidget(self.controlPanel)
        self.radius = 18
        self.setStyleSheet('''
            QMenu {{
                border-radius: {radius}px;
            }}
        '''.format(radius=self.radius))
        self.changeShowPosition()

        # update info use sub-thread
        self.updateThread = QThread()
        self.updateInfo = UpdateInfo(self.updateBatteryInfo)
        self.updateInfo.moveToThread(self.updateThread)
        self.updateThread.started.connect(self.updateInfo.run)
        self.updateInfo.finished.connect(self.updateThread.quit)
        self.updateThread.start()

        # create refresh Timer
        self.timerThread = QThread()
        self.backRefresh = BackRefresh(self.updateBatteryInfo, self.toMillisecond(self.interval, self.scale))
        self.backRefresh.moveToThread(self.timerThread)
        self.timerThread.started.connect(self.backRefresh.run)
        self.timerThread.finished.connect(self.backRefresh.finish)
        self.timerThread.start()

        # create darkMode listener
        self.darkModeThread = QThread()
        self.darkModeListener = DarkModeListener(self.updateBatteryInfo)
        self.darkModeListener.moveToThread(self.darkModeThread)
        self.darkModeThread.started.connect(self.darkModeListener.run)
        self.darkModeThread.start()

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

        if not (min_x < c_x < max_x and min_y < c_y < max_y):
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
            self.quitApp()
        elif reason == QSystemTrayIcon.Trigger:
            self.clickCount += 1
            if self.clickCount % 2:
                self.changeShowPosition()
                self.show()
                self.updateThread.start()
        elif reason == QSystemTrayIcon.Context:
            self.clickCount += 1

    def showTips(self, value):
        QToolTip.showText(QCursor.pos(), str(value))

    def changeShowPosition(self):
        trayPosition = self.tray.geometry()
        x = trayPosition.x() - ((self.window_width - trayPosition.width()) >> 1)
        y = trayPosition.y() - (self.window_height + 20)
        self.move(x, y)

    def getBatteryInfo(self):
        try:
            battery = self.rebt.get_battery()
            isCharge = self.rebt.is_charging()
        except RuntimeError as e:
            battery = 0
            isCharge = 0
            self.tray.showMessage("Error", str(e), self.defaultIcon)
        return battery, isCharge

    def generateIcon(self, battery, isCharge):
        tray = TrayIcon('Tray')
        widget = TrayIcon('Widget')

        if battery == -1:
            return self.defaultIcon, widget.draw(0, isCharge, IconStyle.RECT)

        widgetIcon = widget.draw(battery, isCharge, IconStyle.RECT)

        icon_style = IconStyle(self.rebt.config.getDefault("trayStyle"))

        trayIcon = tray.draw(battery, isCharge, icon_style)
        return trayIcon, widgetIcon

    def updateBatteryInfo(self):
        battery, isCharge = self.getBatteryInfo()

        self.curBattery = battery
        self.chargeStatus = isCharge
        trayIcon, widgetIcon = self.generateIcon(battery, isCharge)
        self.tray.setToolTip(f"{battery}%")
        self.tray.setIcon(trayIcon)
        self.controlPanel.battery.setText(f" {battery}%")
        self.controlPanel.battery.setIcon(widgetIcon)

    def updateInterval(self):
        interval = self.controlPanel.intervalSlider.value()
        self.controlPanel.intervalLabel.setText(str(interval))
        self.backRefresh.intervalChange.emit(self.toMillisecond(interval, self.scale))
        # write to default file
        self.rebt.config.setInterval(interval)
        self.rebt.config.save()

    def updateDevice(self, name):
        deviceInfo = DEVICE[name]
        self.rebt.config.setDevice(name, deviceInfo["usbId"], deviceInfo["tranId"])
        self.rebt.findAll = False
        self.backRefresh.update.emit()
        self.rebt.config.save()

    def toMillisecond(self, interval, scale="seconds"):
        if scale == "seconds":
            return interval * 1000
        if scale == "minutes":
            return interval * 60 * 1000

    def quitApp(self):
        self.darkModeListener.finish()
        self.timerThread.quit()
        self.darkModeThread.quit()
        self.darkModeThread.wait()
        app.quit()


class BackRefresh(QObject):
    finished = Signal()
    intervalChange = Signal(int)

    def __init__(self, func, interval):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(func)

    def finish(self):
        self.timer.stop()

    def run(self):
        self.timer.start()
        self.intervalChange.connect(lambda newInterval: self.timer.setInterval(newInterval))


class UpdateInfo(QObject):
    finished = Signal()

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()
        self.finished.emit()


class DarkModeListener(QObject):
    finished = Signal()

    def __init__(self, func):
        super().__init__()
        self.darkMode = DarkMode()
        self.func = func

    def changeTheme(self, args):
        self.func()

    def finish(self):
        self.darkMode.stop()

    def run(self):
        self.darkMode.listener(self.changeTheme)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
