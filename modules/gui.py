from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import asyncio

from modules import globals, api


class MusicScrubber(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrubbing = False

    def mousePressEvent(self, event):
        self.scrubbing = True
        event.accept()
        x = event.pos().x()
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(value)
        asyncio.get_event_loop().create_task(api.seek(value))

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
        asyncio.get_event_loop().create_task(api.seek(value))


class SoundyGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags())
        self.setWindowIcon(QIcon('resources/icon.png'))
        self.setObjectName(u"Soundy")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(250, 69)

        self.main = QWidget(self)
        self.main.setObjectName(u"main")
        self.main_grid = QGridLayout(self.main)
        self.main_grid.setObjectName(u"main_grid")
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setHorizontalSpacing(0)

        self.cover_art = QLabel(self)
        self.cover_art.setObjectName(u"cover_art")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.cover_art.setSizePolicy(sizePolicy)

        pixmap = QPixmap("resources/icon_small.png")
        self.update_cover_art(pixmap)

        self.main_grid.addWidget(self.cover_art, 0, 0, 1, 1)

        self.info_section = QFrame(self.main)
        self.info_section.setObjectName(u"info_section")
        self.info_section.setMinimumSize(QSize(0, 0))
        self.info_section.setFrameShape(QFrame.NoFrame)
        self.info_section.setFrameShadow(QFrame.Raised)
        self.grid_layout = QGridLayout(self.info_section)
        self.grid_layout.setObjectName(u"grid_layout")
        self.grid_layout.setContentsMargins(0, 14, 6, 0)

        self.title = QLabel(self.info_section)
        self.title.setObjectName(u"title")
        self.title.setFont(globals.font_track)

        self.grid_layout.addWidget(self.title, 0, 0, 1, 1)

        self.artist = QLabel(self.info_section)
        self.artist.setObjectName(u"artist")
        self.artist.setFont(globals.font_artist)

        self.grid_layout.addWidget(self.artist, 1, 0, 1, 1)

        self.time_scrubber = MusicScrubber(self.info_section)
        self.time_scrubber.setObjectName(u"time_scrubber")
        self.time_scrubber.setOrientation(Qt.Horizontal)
        self.time_scrubber.setMaximum(600000)
        self.time_scrubber.setMinimum(0)
        self.time_scrubber.setFixedWidth(181)
        self.time_scrubber.setFixedHeight(10)
        self.time_scrubber.setTickInterval(0)

        self.time_scrubber_mask = QRegion(QRect(0, 0, 181, 10),QRegion.Rectangle)
        width = 181
        height = 10
        radius_br = 5
        rounded = QRegion(width-2*radius_br, height-2*radius_br, 2*radius_br, 2*radius_br, QRegion.Ellipse)
        corner = QRegion(width-radius_br, height-radius_br, radius_br, radius_br, QRegion.Rectangle)
        self.time_scrubber_mask = self.time_scrubber_mask.subtracted(corner.subtracted(rounded))
        self.time_scrubber.setMask(self.time_scrubber_mask)

        # self.time_scrubber_mask = QPixmap(181, 4)
        # self.time_scrubber_mask.fill(QColor("transparent"))
        # painter = QPainter(self.time_scrubber_mask)
        # painter.setRenderHint(QPainter.Antialiasing)
        # painter.setBrush(QColor("#FFFFFFFF"))
        # painter.setPen(Qt.NoPen)
        # painter.drawRoundedRect(-8, -8, 189, 12, 8, 8)
        # painter.end()
        # self.time_scrubber.setMask(self.time_scrubber_mask.mask())

        self.grid_layout.addWidget(self.time_scrubber, 2, 0, 1, 1)


        self.main_grid.addWidget(self.info_section, 0, 1, 1, 1)

        self.setCentralWidget(self.main)

        QMetaObject().connectSlotsByName(self)


        self.setWindowTitle("Soundy")
        self.update_track_name("Soundy")
        self.update_artist_name("By WillyJL")

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def update_cover_art(self, pixmap):
        rounded = QPixmap(pixmap.size())
        rounded.fill(QColor("transparent"))
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 100, 69, 5, 5)
        painter.end()
        self.cover_art.setPixmap(rounded)

    def update_track_name(self, title):
        title = "   " + title
        if self.title.fontMetrics().boundingRect(title).width() > 156:
            cutoff = 1
            while self.title.fontMetrics().boundingRect(title[:-cutoff] + "...").width() > 156:
                cutoff += 1
            self.title.setText(title[:-cutoff] + "...")
            self.title.setToolTip(title)
        else:
            self.title.setText(title)
            self.title.setToolTip("")

    def update_artist_name(self, artist):
        artist = "   " + artist
        if self.artist.fontMetrics().boundingRect(artist).width() > 156:
            cutoff = 1
            while self.artist.fontMetrics().boundingRect(artist[:-cutoff] + "...").width() > 156:
                cutoff += 1
            self.artist.setText(artist[:-cutoff] + "...")
            self.artist.setToolTip(artist)
        else:
            self.artist.setText(artist)
            self.artist.setToolTip("")


QSS = """
#main {
    background: #1E1E1E;
    border-radius: 5px
}

QSlider:horizontal {
}

QSlider::groove:horizontal {
    background: transparent;
    height: 4px;
    subcontrol-position: bottom
}

QSlider::handle:horizontal {
    background: transparent
}

QSlider::add-page:horizontal {
    background: transparent
}

QSlider::sub-page:horizontal {
    background: #696969
}
"""
