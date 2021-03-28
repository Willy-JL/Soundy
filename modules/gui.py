from types import FunctionType
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import asyncio

from modules import globals, api


class MusicScrubber(QSlider):
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


class MusicButton(QPushButton):
    def __init__(self, parent, callback: FunctionType, font, size, default_state: str, buttons: dict):
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


class SoundyGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags())
        self.can_drag = False
        self.setWindowIcon(QIcon('resources/icon.png'))
        self.setObjectName(u"Soundy")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(250, 69)
        self.max_info_width = 171

        self.main = QWidget(self)
        self.main.setObjectName(u"main")
        self.main_grid = QGridLayout(self.main)
        self.main_grid.setObjectName(u"main_grid")
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setHorizontalSpacing(0)

        self.cover_art = QLabel(self)
        self.cover_art.setObjectName(u"cover_art")
        self.cover_art.setFixedSize(69, 69)
        self.update_cover_art()

        self.main_grid.addWidget(self.cover_art, 0, 0, 1, 1)

        self.info_section = QFrame(self.main)
        self.info_section.setObjectName(u"info_section")
        self.info_section.setMinimumSize(QSize(0, 0))
        self.info_section.setFrameShape(QFrame.NoFrame)
        self.info_section.setFrameShadow(QFrame.Raised)
        self.grid_layout = QGridLayout(self.info_section)
        self.grid_layout.setObjectName(u"grid_layout")
        self.grid_layout.setVerticalSpacing(3)
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.spacer_top = QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.grid_layout.addItem(self.spacer_top, 0, 0, 1, 7)

        self.title = QLabel(self.info_section)
        self.title.setObjectName(u"title")
        self.title.setFont(globals.font_track)
        self.title_opacity = QGraphicsOpacityEffect(self.title)
        self.title_opacity.setOpacity(1.0)
        self.title.setGraphicsEffect(self.title_opacity)

        self.grid_layout.addWidget(self.title, 1, 0, 1, 7)

        self.artist = QLabel(self.info_section)
        self.artist.setObjectName(u"artist")
        self.artist.setFont(globals.font_artist)
        self.artist_opacity = QGraphicsOpacityEffect(self.artist)
        self.artist_opacity.setOpacity(1.0)
        self.artist.setGraphicsEffect(self.artist_opacity)

        self.grid_layout.addWidget(self.artist, 2, 0, 1, 7)

        self.time_scrubber = MusicScrubber(self.info_section)
        self.time_scrubber.setObjectName(u"time_scrubber")
        width = 181
        height = 8
        radius_br = 7
        self.time_scrubber.setFixedSize(width, height)
        self.time_scrubber_mask = QRegion(QRect(0, 0, width, height),QRegion.Rectangle)
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

        self.grid_layout.addWidget(self.time_scrubber, 3, 0, 1, 7)

        self.spacer_left = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_layout.addItem(self.spacer_left, 0, 0, 3, 1)

        self.shuffle = MusicButton(self.info_section, print, globals.font_mdi_18, 20, "disabled", {
            "enabled": {
                True:  "󰒝",
                False: "󰒝"
            },
            "disabled": {
                True:  "󰒞",
                False: "󰒞"
            }
        })
        self.shuffle.setObjectName(u"shuffle")
        self.shuffle_opacity = QGraphicsOpacityEffect(self.shuffle)
        self.shuffle_opacity.setOpacity(0.0)
        self.shuffle.setGraphicsEffect(self.shuffle_opacity)

        self.grid_layout.addWidget(self.shuffle, 0, 1, 4, 1)

        self.skip_prev = MusicButton(self.info_section, api.skip_prev, globals.font_mdi_26, 30, "normal", {
            "normal": {
                True:  "󰒮",
                False: "󰼨"
            }
        })
        self.skip_prev.setObjectName(u"skip_prev")
        self.skip_prev_opacity = QGraphicsOpacityEffect(self.skip_prev)
        self.skip_prev_opacity.setOpacity(0.0)
        self.skip_prev.setGraphicsEffect(self.skip_prev_opacity)

        self.grid_layout.addWidget(self.skip_prev, 0, 2, 4, 1)

        self.play_pause = MusicButton(self.info_section, api.play_pause, globals.font_mdi_38, 43, "paused", {
            "playing": {
                True:  "󰏥",
                False: "󰏦"
            },
            "paused": {
                True:  "󰐌",
                False: "󰐍"
            }
        })
        self.play_pause.setObjectName(u"play_pause")
        self.play_pause_opacity = QGraphicsOpacityEffect(self.play_pause)
        self.play_pause_opacity.setOpacity(0.0)
        self.play_pause.setGraphicsEffect(self.play_pause_opacity)

        self.grid_layout.addWidget(self.play_pause, 0, 3, 4, 1)

        self.skip_next = MusicButton(self.info_section, api.skip_next, globals.font_mdi_26, 30, "normal", {
            "normal": {
                True:  "󰒭",
                False: "󰼧"
            }
        })
        self.skip_next.setObjectName(u"skip_next")
        self.skip_next_opacity = QGraphicsOpacityEffect(self.skip_next)
        self.skip_next_opacity.setOpacity(0.0)
        self.skip_next.setGraphicsEffect(self.skip_next_opacity)

        self.grid_layout.addWidget(self.skip_next, 0, 4, 4, 1)

        self.repeat = MusicButton(self.info_section, print, globals.font_mdi_18, 20, "disabled", {
            "queue": {
                True:  "󰑖",
                False: "󰑖"
            },
            "single": {
                True:  "󰑘",
                False: "󰑘"
            },
            "disabled": {
                True:  "󰑗",
                False: "󰑗"
            }
        })
        self.repeat.setObjectName(u"repeat")
        self.repeat_opacity = QGraphicsOpacityEffect(self.repeat)
        self.repeat_opacity.setOpacity(0.0)
        self.repeat.setGraphicsEffect(self.repeat_opacity)

        self.grid_layout.addWidget(self.repeat, 0, 5, 4, 1)

        self.spacer_right = QSpacerItem(24, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_layout.addItem(self.spacer_right, 0, 6, 3, 1)


        self.close_button = MusicButton(self.info_section, lambda: globals.gui.close(), globals.font_mdi_13, 15, "normal", {
            "normal": {
                True:  "󰅙",
                False: "󰅚"
            }
        })
        self.close_button.setObjectName(u"close_button")
        self.close_button_opacity = QGraphicsOpacityEffect(self.close_button)
        self.close_button_opacity.setOpacity(0.0)
        self.close_button.setGraphicsEffect(self.close_button_opacity)

        self.close_button.move(161, 4)
        # self.grid_layout.addWidget(self.close_button, 0, 6, 3, 1)


        self.main_grid.addWidget(self.info_section, 0, 1, 1, 1)

        self.setCentralWidget(self.main)

        QMetaObject().connectSlotsByName(self)


        self.setWindowTitle("Soundy")
        self.update_track_name("Soundy")
        self.update_artist_name("By WillyJL")

    def closeEvent(self, event):
        globals.loop.stop()
        event.accept()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()
        self.can_drag = True

    def mouseReleaseEvent(self, event):
        self.can_drag = False

    def mouseMoveEvent(self, event):
        if self.can_drag:
            delta = QPoint (event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def enterEvent(self, event):
        asyncio.get_event_loop().create_task(self.toggle_controls(True))

    def leaveEvent(self, event):
        asyncio.get_event_loop().create_task(self.toggle_controls(False))

    async def toggle_controls(self, toggle):
        anim_list = [
            [QPropertyAnimation(self.title_opacity,        b"opacity"), False],
            [QPropertyAnimation(self.artist_opacity,       b"opacity"), False],
            [QPropertyAnimation(self.shuffle_opacity,      b"opacity"), True ],
            [QPropertyAnimation(self.skip_prev_opacity,    b"opacity"), True ],
            [QPropertyAnimation(self.play_pause_opacity,   b"opacity"), True ],
            [QPropertyAnimation(self.skip_next_opacity,    b"opacity"), True ],
            [QPropertyAnimation(self.repeat_opacity,       b"opacity"), True ],
            [QPropertyAnimation(self.close_button_opacity, b"opacity"), True ]
        ]
        for anim in anim_list:
            anim[0].setDuration(100)
            anim_toggle = toggle
            if anim[1]:
                anim_toggle = not anim_toggle
            if anim_toggle:
                anim[0].setStartValue(1.0)
                anim[0].setEndValue(0.0)
            else:
                anim[0].setStartValue(0.0)
                anim[0].setEndValue(1.0)
        for anim in anim_list:
            anim[0].start()
        await asyncio.sleep(0.2)  # Wait for animation to finish
        for anim in anim_list:
            vis_toggle = not toggle
            if anim[1]:
                vis_toggle = not vis_toggle
            anim[0].targetObject().parent().setVisible(vis_toggle)

    def update_cover_art(self, thumbnail=[None, None]):
        if thumbnail[0]:
            pixmap = thumbnail[0]
            globals.blank_cover_art = False
        else:
            pixmap = QPixmap("resources/icon_small.png")
            globals.blank_cover_art = True
        rounded = QPixmap(pixmap.size())
        rounded.fill(QColor("transparent"))
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 100, 69, 5, 5)
        painter.end()
        self.cover_art.setPixmap(rounded)
        if thumbnail[0]:
            self.update_style(thumbnail[1][0], thumbnail[1][1])
        else:
            self.update_style()

    def update_track_name(self, title):
        title = "   " + title
        if self.title.fontMetrics().boundingRect(title).width() > self.max_info_width:
            cutoff = 1
            while self.title.fontMetrics().boundingRect(title[:-cutoff] + "...").width() > self.max_info_width:
                cutoff += 1
            self.title.setText(title[:-cutoff] + "...")
        else:
            self.title.setText(title)

    def update_artist_name(self, artist):
        artist = "   " + artist
        if self.artist.fontMetrics().boundingRect(artist).width() > self.max_info_width:
            cutoff = 1
            while self.artist.fontMetrics().boundingRect(artist[:-cutoff] + "...").width() > self.max_info_width:
                cutoff += 1
            self.artist.setText(artist[:-cutoff] + "...")
        else:
            self.artist.setText(artist)

    def update_style(self, ground=None, accent=None):
        if ground:
            ground = '#%02x%02x%02x' % ground[0]
        if accent:
            accent = '#%02x%02x%02x' % accent[0]
        globals.app.setStyleSheet("""
#main {
    background: """ + (ground if ground else "#1E1E1E") + """;
    border-radius: 5px
}

QPushButton {
    border: none
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
    background: """ + (accent if accent else "#696969") + """
}

QLabel {
    color: """ + (accent if accent else "#868686") + """
}

QPushButton {
    color: """ + (accent if accent else "#868686") + """
}
""")
