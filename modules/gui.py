
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import asyncio
from qasync import asyncClose
from functools import partial
from modules import globals, api



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
        self.main_grid.setContentsMargins(0, 0, 6, 0)

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
        self.grid_layout.setContentsMargins(6, 14, 6, 10)

        self.title = QLabel(self.info_section)
        self.title.setObjectName(u"title")
        self.title.setFont(globals.font_track)

        self.grid_layout.addWidget(self.title, 0, 0, 1, 1)

        self.artist = QLabel(self.info_section)
        self.artist.setObjectName(u"artist")
        self.artist.setFont(globals.font_artist)

        self.grid_layout.addWidget(self.artist, 1, 0, 1, 1)


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
        painter.drawRoundedRect(0, 0, 100, 69, 8, 8)
        painter.end()
        self.cover_art.setPixmap(rounded)

    def update_track_name(self, title):
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
    border-radius: 8px
}
"""
