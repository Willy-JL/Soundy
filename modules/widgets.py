from types import FunctionType
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import asyncio

from modules import globals, api


class DynamicButton(QPushButton):
    def __init__(self, parent, callback: FunctionType, font, size, default_state, buttons: dict):
        super().__init__(parent)
        self.hovered = False
        self.buttons = buttons
        self.state = default_state
        self.setText(self.buttons[self.state][self.hovered])
        self.setFont(font)
        self.setFixedSize(size, size)
        self.clicked.connect(callback)

    def enterEvent(self, event):
        self.hovered = True
        self.update_text()

    def leaveEvent(self, event):
        self.hovered = False
        self.update_text()

    def set_state(self, state):
        self.state = state
        self.update_text()

    def update_text(self):
        self.setText(self.buttons[self.state][self.hovered])


class TimeScrubber(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrubbing = False
        self.setOrientation(Qt.Horizontal)
        self.setMaximum(600000)
        self.setMinimum(0)

    def mousePressEvent(self, event):
        self.scrubbing = True
        event.accept()
        x = event.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(value)
        globals.loop.create_task(api.seek(value))

    def mouseMoveEvent(self, event):
        self.scrubbing = True
        event.accept()
        x = event.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(value)

    def mouseReleaseEvent(self, event):
        self.scrubbing = False
        event.accept()
        x = event.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(value)
        globals.loop.create_task(api.seek(value))


class MarqueeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label_x = 0
        self.scrolling = False

    def setColor(self, color):
        self.color = QColor(color)

    def reset(self):
        self.label_x = 0
        self.scrolling = False

    async def marquee(self):
        label_width = self.fontMetrics().boundingRect(self.text()).width()
        if label_width > globals.gui.max_info_width:
            self.label_x = -1
            self.scrolling = True
            while self.scrolling:
                if self.label_x == 0:
                    self.scrolling = False
                    break
                elif self.label_x > -label_width:
                    self.label_x -= 1
                else:
                    self.label_x = self.width()
                self.repaint()
                await asyncio.sleep(0.02)
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())
        painter.setPen(self.color)
        painter.drawText(self.label_x, self.height() - 7, self.text())


class MouseTransparentWidget(QWidget):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        region = QRegion(self.frameGeometry())
        region -= QRegion(self.geometry())
        region += self.childrenRegion()
        self.setMask(region)
