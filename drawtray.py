from PySide2.QtCore import Qt, QRect, QRectF, QSize
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

    def drawNumIcon(self, battery):
        ft = QFont("Microsoft YaHei", 56)
        ft_rect = QFontMetrics(ft).boundingRect(str(battery))
        scale = ft_rect.width() / self.pixmap.width()
        if scale > 1:
            ft.setPointSize(36)
        elif scale < 0.5:
            ft.setPointSize(62)
        self.painter.setFont(ft)
        self.painter.setRenderHint(QPainter.HighQualityAntialiasing)
        self.painter.drawText(self.pixmap.rect(), Qt.AlignCenter, str(battery))
        self.painter.end()

    def drawRectIcon(self, battery):
        self.painter.setBrush(Qt.black)
        self.painter.setPen(Qt.transparent)
        brt = self.drawRoundedRect((19, 42), 6)

        self.painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        percentage = battery / 100
        mask_x = brt.x() + percentage * brt.width()
        mask_width = brt.width() * (1 - percentage)
        maskBrt = QRectF(mask_x, brt.y(), mask_width, brt.height())
        self.painter.fillRect(maskBrt, Qt.transparent)

        # big rect
        self.painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        self.painter.setPen(QPen(Qt.black, 10))
        self.painter.setBrush(Qt.transparent)
        self.drawRoundedRect((3, 28), 16)
        self.painter.end()

    def draw(self, battery, style=0):
        if style == 0:
            self.drawNumIcon(battery)
        else:
            self.drawRectIcon(battery)
        return self.pixmap
