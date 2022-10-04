from PySide2.QtCore import Qt, QRect, QRectF, QSize, QPointF
from PySide2.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QFontMetrics
from PySide2.QtWidgets import QApplication


class TrayIcon:

    def __init__(self):
        self.bgWidth = 128
        self.bgHeight = 128
        self.pixmap = QPixmap(self.bgWidth, self.bgHeight)
        self.pixmap.fill(Qt.transparent)
        self.painter = QPainter(self.pixmap)

    def centerWidth(self, width):
        return (self.bgWidth - width) >> 1

    def centerHeight(self, height):
        return (self.bgHeight - height) >> 1

    def drawRoundedRect(self, margin, radius, battery=1.0):
        marginX = margin[0]
        marginY = margin[1]
        bRectWidth = self.bgWidth - marginX * 2
        bRectHeight = self.bgHeight - marginY * 2
        brt = QRectF(self.centerWidth(bRectWidth), self.centerHeight(bRectHeight), bRectWidth * battery, bRectHeight)
        self.painter.drawRoundedRect(brt, radius, radius)
        return brt

    def drawChord(self, brt):
        width = height = 15
        cr = QRectF(brt.x() + brt.width() - 5, self.centerHeight(height), width, height)
        self.painter.drawChord(cr, 90 * 16, -180 * 16)

    def drawChargeIcon(self, r=20):
        p = QRectF(self.pixmap.width() - r, 0, r, r)
        self.painter.setPen(Qt.red)
        self.painter.setBrush(Qt.red)
        self.painter.drawChord(p, 0, 360 * 16)

    def drawNumIcon(self, battery, isCharge):
        if isCharge: self.drawChargeIcon(26)
        ft = QFont("Microsoft YaHei", 48)
        ft_rect = QFontMetrics(ft).boundingRect(str(battery))
        scale = ft_rect.width() / self.pixmap.width()
        if scale > 1:
            ft.setPointSize(36)
        elif scale < 0.5:
            ft.setPointSize(62)
        self.painter.setFont(ft)
        self.painter.setPen(Qt.black)
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)
        self.painter.drawText(self.pixmap.rect(), Qt.AlignCenter, str(battery))

        self.painter.end()

    def drawRectIcon(self, battery, isCharge):
        self.painter.setBrush(Qt.black)
        self.painter.setPen(Qt.transparent)
        brt = self.drawRoundedRect((16, 42), 6)

        self.painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        percentage = battery / 100
        mask_x = brt.x() + percentage * brt.width()
        mask_width = brt.width() * (1 - percentage)
        maskBrt = QRectF(mask_x, brt.y(), mask_width, brt.height())
        self.painter.fillRect(maskBrt, Qt.transparent)

        # big rect
        self.painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        self.painter.setPen(QPen(Qt.black, 9))
        self.painter.setBrush(Qt.transparent)
        brt_ = self.drawRoundedRect((6, 30), 16)
        if isCharge: self.drawChargeIcon()
        self.painter.end()

    def draw(self, battery, isCharge, style=0):
        if style == 0:
            self.drawNumIcon(battery, isCharge)
        else:
            self.drawRectIcon(battery, isCharge)
        return self.pixmap
