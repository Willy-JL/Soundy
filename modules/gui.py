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
    def __init__(self, parent, normal_text, hover_text, callback):
        super().__init__(parent)
        self.hovered = False
        self.hover_text = hover_text
        self.normal_text = normal_text
        self.setText(self.normal_text)
        self.setFont(globals.font_mdi)
        self.setFixedSize(30, 30)
        self.clicked.connect(callback)

    def enterEvent(self, event):
        self.hovered = True
        self.update_text()

    def leaveEvent(self, event):
        self.hovered = False
        self.update_text()

    def update_text(self):
        if self.hovered:
            self.setText(self.hover_text)
        else:
            self.setText(self.normal_text) 


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
        self.grid_layout.setVerticalSpacing(3)
        self.grid_layout.setContentsMargins(0, 14, 6, 0)

        self.title = QLabel(self.info_section)
        self.title.setObjectName(u"title")
        self.title.setFont(globals.font_track)
        self.title_opacity = QGraphicsOpacityEffect(self.title)
        self.title_opacity.setOpacity(1.0)
        self.title.setGraphicsEffect(self.title_opacity)

        self.grid_layout.addWidget(self.title, 0, 0, 1, 5)

        self.artist = QLabel(self.info_section)
        self.artist.setObjectName(u"artist")
        self.artist.setFont(globals.font_artist)
        self.artist_opacity = QGraphicsOpacityEffect(self.artist)
        self.artist_opacity.setOpacity(1.0)
        self.artist.setGraphicsEffect(self.artist_opacity)

        self.grid_layout.addWidget(self.artist, 1, 0, 1, 5)

        self.time_scrubber = MusicScrubber(self.info_section)
        self.time_scrubber.setObjectName(u"time_scrubber")
        width = 181
        height = 10
        radius_br = 5
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

        self.grid_layout.addWidget(self.time_scrubber, 2, 0, 1, 5)


        self.shuffle = MusicButton(self.info_section, '󰒟', '󰒟', print)
        self.shuffle.setObjectName(u"shuffle")
        self.shuffle_opacity = QGraphicsOpacityEffect(self.shuffle)
        self.shuffle_opacity.setOpacity(0.0)
        self.shuffle.setGraphicsEffect(self.shuffle_opacity)

        self.grid_layout.addWidget(self.shuffle, 0, 0, 2, 1)

        self.skip_prev = MusicButton(self.info_section, '󰼨', '󰒮', api.skip_prev)
        self.skip_prev.setObjectName(u"skip_prev")
        self.skip_prev_opacity = QGraphicsOpacityEffect(self.skip_prev)
        self.skip_prev_opacity.setOpacity(0.0)
        self.skip_prev.setGraphicsEffect(self.skip_prev_opacity)

        self.grid_layout.addWidget(self.skip_prev, 0, 1, 2, 1)

        self.play_pause = MusicButton(self.info_section, '󰏦', '󰏥', api.play_pause)
        self.play_pause.setObjectName(u"play_pause")
        self.play_pause_opacity = QGraphicsOpacityEffect(self.play_pause)
        self.play_pause_opacity.setOpacity(0.0)
        self.play_pause.setGraphicsEffect(self.play_pause_opacity)

        self.grid_layout.addWidget(self.play_pause, 0, 2, 2, 1)

        self.skip_next = MusicButton(self.info_section, '󰼧', '󰒭', api.skip_next)
        self.skip_next.setObjectName(u"skip_next")
        self.skip_next_opacity = QGraphicsOpacityEffect(self.skip_next)
        self.skip_next_opacity.setOpacity(0.0)
        self.skip_next.setGraphicsEffect(self.skip_next_opacity)

        self.grid_layout.addWidget(self.skip_next, 0, 3, 2, 1)

        self.repeat = MusicButton(self.info_section, '󰑖', '󰑖', print)
        self.repeat.setObjectName(u"repeat")
        self.repeat_opacity = QGraphicsOpacityEffect(self.repeat)
        self.repeat_opacity.setOpacity(0.0)
        self.repeat.setGraphicsEffect(self.repeat_opacity)

        self.grid_layout.addWidget(self.repeat, 0, 4, 2, 1)


        self.main_grid.addWidget(self.info_section, 0, 1, 1, 1)

        self.setCentralWidget(self.main)

        QMetaObject().connectSlotsByName(self)


        self.setWindowTitle("Soundy")
        self.update_track_name("Soundy")
        self.update_artist_name("By WillyJL")

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
        # self.toggle_controls(True)

    def leaveEvent(self, event):
        asyncio.get_event_loop().create_task(self.toggle_controls(False))
        # self.toggle_controls(False)

    async def toggle_controls(self, toggle):
        anim_list = [
            [QPropertyAnimation(self.title_opacity,      b"opacity"), False],
            [QPropertyAnimation(self.artist_opacity,     b"opacity"), False],
            [QPropertyAnimation(self.shuffle_opacity,    b"opacity"), True ],
            [QPropertyAnimation(self.skip_prev_opacity,  b"opacity"), True ],
            [QPropertyAnimation(self.play_pause_opacity, b"opacity"), True ],
            [QPropertyAnimation(self.skip_next_opacity,  b"opacity"), True ],
            [QPropertyAnimation(self.repeat_opacity,     b"opacity"), True ],
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

    def update_cover_art(self, pixmap=None):
        if pixmap:
            pmap = pixmap
        else:
            pmap = QPixmap("resources/icon_small.png")
        rounded = QPixmap(pmap.size())
        rounded.fill(QColor("transparent"))
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 100, 69, 5, 5)
        painter.end()
        self.cover_art.setPixmap(rounded)
        if pixmap:
            self.update_style()
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

    def update_style(self, accent=None, ground=None):
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
""")
