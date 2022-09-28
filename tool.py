import sys
import time
import resource
from drawtray import TrayIcon
from storage import DEVICE
from controller import Rebt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QToolTip
from PySide2.QtCore import Qt, QRectF, QTimer, QObject, Signal, QThread
from PySide2.QtGui import QIcon, QPainterPath, QRegion, QTransform, QCursor, QPixmap, QPainter, QFont


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Icon
        self.full = QIcon(':/resource/imgs/full.svg')
        self.most = QIcon(':/resource/imgs/most.svg')
        self.half = QIcon(':/resource/imgs/half.svg')
        self.low = QIcon(':/resource/imgs/low.svg')
        self.empty = QIcon(':/resource/imgs/empty.svg')
        self.defaultIcon = QIcon(':/resource/imgs/icon.png')
        self.setWindowIcon(self.defaultIcon)
        self.clickCount = 0

        # Init System tray
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.defaultIcon)
        self.tray.activated.connect(self.trigger)
        self.tray.setVisible(True)
        try:
            self.rebt = Rebt()
            self.minutes = self.rebt.config.getDefault("interval")
        except RuntimeError as e:
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
        self.controlPanel = QUiLoader().load(':/resource/tool.ui')
        self.controlPanel.setFixedSize(self.window_width, self.window_height)
        self.controlPanel.closeButton.clicked.connect(app.quit)
        self.controlPanel.intervalSlider.setValue(self.minutes)
        self.controlPanel.intervalLabel.setText(str(self.minutes))
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

        # create refresh thread
        self.refreshThread = QThread()
        self.refreshWorker = RefreshWorker(self.updateBatteryInfo)
        self.refreshWorker.moveToThread(self.refreshThread)
        self.refreshThread.started.connect(self.refreshWorker.run)
        self.refreshWorker.finished.connect(self.refreshThread.quit)
        # refresh now
        self.refreshThread.start()

        # Init refresh Timer
        self.timer = QTimer()
        self.timer.setInterval(self.toMillisecond(self.minutes))
        self.timer.timeout.connect(self.refreshThread.start)
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
            app.quit()
        elif reason == QSystemTrayIcon.Trigger:
            self.clickCount += 1
            if self.clickCount % 2:
                self.changeShowPosition()
                self.show()
                self.refreshThread.start()

    def showTips(self, value):
        QToolTip.showText(QCursor.pos(), str(value))

    def drawTrayIcon(self, battery):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setFont(QFont("Microsoft YaHei", 26))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, str(battery))
        painter.end()
        return pixmap

    def changeShowPosition(self):
        trayPosition = self.tray.geometry()
        x = trayPosition.x() - ((self.window_width - trayPosition.width()) >> 1)
        y = trayPosition.y() - (self.window_height + 20)
        self.move(x, y)

    def getBatteryInfo(self):
        try:
            battery = self.rebt.get_battery()
        except RuntimeError as e:
            battery = 0
            self.tray.showMessage("Error", str(e), self.defaultIcon)

        if battery == -1:
            return self.defaultIcon, TrayIcon().draw(0, 1), 0

        if self.rebt.config.getDefault("trayStyle") == 1:
            trayIcon = widgetIcon = TrayIcon().draw(battery, 1)
        else:
            trayIcon = TrayIcon().draw(battery, 0)
            widgetIcon = TrayIcon().draw(battery, 1)
        return trayIcon, widgetIcon, battery

    def updateBatteryInfo(self):
        trayIcon, widgetIcon, battery = self.getBatteryInfo()
        self.tray.setToolTip(f"{battery}%")
        self.tray.setIcon(trayIcon)
        self.controlPanel.battery.setText(f' {battery}%')
        self.controlPanel.battery.setIcon(widgetIcon)

    def updateInterval(self):
        minutes = self.controlPanel.intervalSlider.value()
        self.controlPanel.intervalLabel.setText(str(minutes))
        self.timer.setInterval(self.toMillisecond(minutes))
        # write to default file
        self.rebt.config.setInterval(minutes)
        self.rebt.config.save()

    def updateDevice(self, name):
        deviceInfo = DEVICE[name]
        self.rebt.config.setDevice(name, deviceInfo["usbId"], deviceInfo["tranId"])
        self.rebt.findAll = False
        self.refreshThread.start()
        self.rebt.config.save()

    def toMillisecond(self, minutes):
        return minutes * 60 * 1000


class RefreshWorker(QObject):
    finished = Signal()

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        if self.func:
            self.func()
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
