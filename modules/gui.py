from PyQt5.QtWidgets import *
from qasync import asyncSlot
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import webbrowser
import asyncio
import sys

from modules import globals, api, widgets


class SoundyGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags())
        self.can_drag = False
        self.setWindowIcon(QIcon('resources/icons/icon.png'))
        self.setObjectName(u"Soundy")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        if globals.settings.value("alwaysOnTop", 1):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if globals.settings.value("compactMode", 1):
            self.setFixedSize(250, 69)
        else:
            self.setFixedSize(250, 126)
        self.max_info_width = 169

        self.main = QWidget(self)
        self.main.setObjectName(u"main")
        self.main_grid = QGridLayout(self.main)
        self.main_grid.setObjectName(u"main_grid")
        if globals.settings.value("compactMode", 1):
            self.main_grid.setContentsMargins(0, 0, 0, 0)
        else:
            self.main_grid.setContentsMargins(0, 8, 0, 0)
        self.main_grid.setHorizontalSpacing(0)

        self.cover_art = QLabel(self)
        self.cover_art.setObjectName(u"cover_art")
        self.cover_art.setFixedSize(69, 69)

        self.main_grid.addWidget(self.cover_art, 1, 0, 1, 1)


        self.info_section = QWidget(self.main)
        self.info_section.setObjectName(u"info_section")
        self.info_section.setContentsMargins(0, 0, 0, 0)
        self.info_layout = QVBoxLayout(self.info_section)
        self.info_layout.setObjectName(u"info_layout")
        self.info_layout.setSpacing(2)
        self.info_layout.setContentsMargins(0, 4, 0, 0)

        self.title = widgets.MarqueeLabel(self.info_section)
        self.title.setObjectName(u"title")
        self.title.setFont(globals.font_track)
        self.title_opacity = QGraphicsOpacityEffect(self.title)
        self.title_opacity.setOpacity(1.0)
        self.title.setGraphicsEffect(self.title_opacity)

        self.info_layout.addWidget(self.title, stretch=0, alignment=Qt.AlignLeft)

        self.artist = widgets.MarqueeLabel(self.info_section)
        self.artist.setObjectName(u"artist")
        self.artist.setFont(globals.font_artist)
        self.artist_opacity = QGraphicsOpacityEffect(self.artist)
        self.artist_opacity.setOpacity(1.0)
        self.artist.setGraphicsEffect(self.artist_opacity)

        self.info_layout.addWidget(self.artist, stretch=0, alignment=Qt.AlignLeft)

        self.time_scrubber = widgets.MusicScrubber(self.info_section)
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
        self.time_scrubber_opacity = QGraphicsOpacityEffect(self.time_scrubber)
        self.time_scrubber_opacity.setOpacity(1.0)
        self.time_scrubber.setGraphicsEffect(self.time_scrubber_opacity)

        self.info_layout.addWidget(self.time_scrubber, stretch=0, alignment=Qt.AlignLeft)

        self.main_grid.addWidget(self.info_section, 1, 1, 1, 1)


        self.controls_section = QWidget(self.main)
        self.controls_section.setObjectName(u"controls_section")
        self.controls_section.setContentsMargins(0, 0, 0, 0)
        self.controls_layout = QHBoxLayout(self.controls_section)
        self.controls_layout.setObjectName(u"controls_section")
        self.controls_layout.setSpacing(0)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)

        self.spacer_left = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.controls_layout.addItem(self.spacer_left)

        self.shuffle = widgets.MusicButton(self.controls_section, api.set_shuffle, globals.font_mdi_18, 20, False, {
            True: {
                True:  "󰒝",
                False: "󰒝"
            },
            False: {
                True:  "󰒞",
                False: "󰒞"
            }
        })
        self.shuffle.setObjectName(u"shuffle")
        self.shuffle_opacity = QGraphicsOpacityEffect(self.shuffle)
        self.shuffle_opacity.setOpacity(0.0)
        self.shuffle.setGraphicsEffect(self.shuffle_opacity)

        self.controls_layout.addWidget(self.shuffle)

        self.skip_prev = widgets.MusicButton(self.controls_section, api.skip_prev, globals.font_mdi_26, 30, "normal", {
            "normal": {
                True:  "󰒮",
                False: "󰼨"
            }
        })
        self.skip_prev.setObjectName(u"skip_prev")
        self.skip_prev_opacity = QGraphicsOpacityEffect(self.skip_prev)
        self.skip_prev_opacity.setOpacity(0.0)
        self.skip_prev.setGraphicsEffect(self.skip_prev_opacity)

        self.controls_layout.addWidget(self.skip_prev)

        self.play_pause = widgets.MusicButton(self.controls_section, api.play_pause, globals.font_mdi_38, 43, False, {
            True: {
                True:  "󰏥",
                False: "󰏦"
            },
            False: {
                True:  "󰐌",
                False: "󰐍"
            }
        })
        self.play_pause.setObjectName(u"play_pause")
        self.play_pause_opacity = QGraphicsOpacityEffect(self.play_pause)
        self.play_pause_opacity.setOpacity(0.0)
        self.play_pause.setGraphicsEffect(self.play_pause_opacity)

        self.controls_layout.addWidget(self.play_pause)

        self.skip_next = widgets.MusicButton(self.controls_section, api.skip_next, globals.font_mdi_26, 30, "normal", {
            "normal": {
                True:  "󰒭",
                False: "󰼧"
            }
        })
        self.skip_next.setObjectName(u"skip_next")
        self.skip_next_opacity = QGraphicsOpacityEffect(self.skip_next)
        self.skip_next_opacity.setOpacity(0.0)
        self.skip_next.setGraphicsEffect(self.skip_next_opacity)

        self.controls_layout.addWidget(self.skip_next)

        self.repeat = widgets.MusicButton(self.controls_section, api.set_repeat, globals.font_mdi_18, 20, 0, {
            2: {
                True:  "󰑖",
                False: "󰑖"
            },
            1: {
                True:  "󰑘",
                False: "󰑘"
            },
            0: {
                True:  "󰑗",
                False: "󰑗"
            }
        })
        self.repeat.setObjectName(u"repeat")
        self.repeat_opacity = QGraphicsOpacityEffect(self.repeat)
        self.repeat_opacity.setOpacity(0.0)
        self.repeat.setGraphicsEffect(self.repeat_opacity)

        self.controls_layout.addWidget(self.repeat)

        self.spacer_right = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.controls_layout.addItem(self.spacer_right)

        if globals.settings.value("compactMode", 1):
            self.main_grid.addWidget(self.controls_section, 1, 1, 1, 1)
        else:
            self.main_grid.addWidget(self.controls_section, 0, 0, 1, 2)


        self.close_button = widgets.MusicButton(self.main, lambda: globals.gui.close(), globals.font_mdi_13, 15, "normal", {
            "normal": {
                True:  "󰅙",
                False: "󰅚"
            }
        })
        self.close_button.setObjectName(u"close_button")
        self.close_button_opacity = QGraphicsOpacityEffect(self.close_button)
        self.close_button_opacity.setOpacity(0.0)
        self.close_button.setGraphicsEffect(self.close_button_opacity)

        self.close_button.move(228, 6)

        self.settings_button = widgets.MusicButton(self.main, lambda: globals.settings_gui.show(), globals.font_mdi_13, 15, "normal", {
            "normal": {
                True:  "󰒓",
                False: "󰢻"
            }
        })
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button_opacity = QGraphicsOpacityEffect(self.settings_button)
        self.settings_button_opacity.setOpacity(0.0)
        self.settings_button.setGraphicsEffect(self.settings_button_opacity)

        if globals.settings.value("compactMode", 1):
            self.settings_button.move(75, 6)
        else:
            self.settings_button.move(6, 6)

        self.compact_button = widgets.MusicButton(self.main, self.toggle_compact_mode, globals.font_mdi_13, 15, globals.settings.value("compactMode", 1), {
            1: {
                True:  "󰬬",
                False: "󰬭"
            },
            0: {
                True:  "󰬦",
                False: "󰬧"
            }
        })
        self.compact_button.setObjectName(u"compact_button")
        self.compact_button_opacity = QGraphicsOpacityEffect(self.compact_button)
        self.compact_button_opacity.setOpacity(0.0)
        self.compact_button.setGraphicsEffect(self.compact_button_opacity)

        if globals.settings.value("compactMode", 1):
            self.compact_button.move(3, 3)
        else:
            self.compact_button.move(3, 60)


        self.fade_left = QWidget(self.main)
        self.fade_left.setObjectName(u"fade_left")
        self.fade_left.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.fade_left_opacity = QGraphicsOpacityEffect(self.fade_left)
        self.fade_left_opacity.setOpacity(1.0)
        self.fade_left.setGraphicsEffect(self.fade_left_opacity)

        self.main_grid.addWidget(self.fade_left, 1, 1, 1, 1)

        self.fade_right = QWidget(self.main)
        self.fade_right.setObjectName(u"fade_right")
        self.fade_right.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.fade_right_opacity = QGraphicsOpacityEffect(self.fade_right)
        self.fade_right_opacity.setOpacity(1.0)
        self.fade_right.setGraphicsEffect(self.fade_right_opacity)

        self.main_grid.addWidget(self.fade_right, 1, 1, 1, 1)


        self.setCentralWidget(self.main)

        QMetaObject().connectSlotsByName(self)

        if globals.settings.value("geometry"):
            self.restoreGeometry(globals.settings.value("geometry"))
        if globals.settings.value("windowState"):
            self.restoreState(globals.settings.value("windowState"))

        self.setWindowTitle("Soundy")
        self.update_track_info()
        self.update_cover_art()
        globals.loop.create_task(self.toggle_controls(True, True))

    def closeEvent(self, event):
        api.exit_handler(event)

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

    @asyncSlot()
    async def toggle_compact_mode(self, *args):
        globals.settings.setValue("compactMode", int(not bool(globals.settings.value("compactMode", 1))))
        self.compact_button.set_state(globals.settings.value("compactMode", 1))
        if globals.settings.value("compactMode", 1):
            self.setFixedSize(250, 69)
            self.move(self.x(), self.y()+57)
            self.main_grid.setContentsMargins(0, 0, 0, 0)
            self.main_grid.removeWidget(self.controls_section)
            self.main_grid.addWidget(self.controls_section, 1, 1, 1, 1)
            self.close_button.move(228, 6)
            self.settings_button.move(75, 6)
            self.compact_button.move(3, 3)
        else:
            self.setFixedSize(250, 126)
            self.move(self.x(), self.y()-57)
            self.main_grid.setContentsMargins(0, 8, 0, 0)
            self.main_grid.removeWidget(self.controls_section)
            self.main_grid.addWidget(self.controls_section, 0, 0, 1, 2)
            self.close_button.move(228, 6)
            self.settings_button.move(6, 6)
            self.compact_button.move(3, 60)
        await self.toggle_controls(True, True)

    async def toggle_controls(self, toggle, update=False):
        if globals.settings.value("compactMode", 1):
            anim_list = [
                [QPropertyAnimation(self.title_opacity,           b"opacity"), False],
                [QPropertyAnimation(self.artist_opacity,          b"opacity"), False],
                [QPropertyAnimation(self.fade_left_opacity,       b"opacity"), False],
                [QPropertyAnimation(self.fade_right_opacity,      b"opacity"), False],
                [QPropertyAnimation(self.shuffle_opacity,         b"opacity"), True ],
                [QPropertyAnimation(self.skip_prev_opacity,       b"opacity"), True ],
                [QPropertyAnimation(self.play_pause_opacity,      b"opacity"), True ],
                [QPropertyAnimation(self.skip_next_opacity,       b"opacity"), True ],
                [QPropertyAnimation(self.repeat_opacity,          b"opacity"), True ],
                [QPropertyAnimation(self.settings_button_opacity, b"opacity"), True ],
                [QPropertyAnimation(self.close_button_opacity,    b"opacity"), True ],
                [QPropertyAnimation(self.compact_button_opacity,  b"opacity"), True ]
            ]
        else:
            if update:
                anim_list = [
                    [QPropertyAnimation(self.title_opacity,           b"opacity"), True ],
                    [QPropertyAnimation(self.artist_opacity,          b"opacity"), True ],
                    [QPropertyAnimation(self.fade_left_opacity,       b"opacity"), True ],
                    [QPropertyAnimation(self.fade_right_opacity,      b"opacity"), True ],
                    [QPropertyAnimation(self.shuffle_opacity,         b"opacity"), True ],
                    [QPropertyAnimation(self.skip_prev_opacity,       b"opacity"), True ],
                    [QPropertyAnimation(self.play_pause_opacity,      b"opacity"), True ],
                    [QPropertyAnimation(self.skip_next_opacity,       b"opacity"), True ],
                    [QPropertyAnimation(self.repeat_opacity,          b"opacity"), True ],
                    [QPropertyAnimation(self.settings_button_opacity, b"opacity"), True ],
                    [QPropertyAnimation(self.close_button_opacity,    b"opacity"), True ],
                    [QPropertyAnimation(self.compact_button_opacity,  b"opacity"), True ]
                ]
            else:
                anim_list = [
                    [QPropertyAnimation(self.compact_button_opacity,  b"opacity"), True ]
                ]
        for anim in anim_list:
            anim[0].setDuration(75)
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
        await asyncio.sleep(0.15)  # Wait for animation to finish

    def update_cover_art(self, thumbnail=[None, None]):
        if thumbnail[0]:
            pixmap = thumbnail[0]
            globals.blank_cover_art = False
        else:
            pixmap = QPixmap("resources/icons/icon_small.png")
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

    def update_track_info(self, title="", artist=""):
        if not title and not artist:
            title = f"Soundy v{globals.version}"
            artist = "By WillyJL" + (f" - Hiding in {globals.timeout}" if globals.settings.value("autoHide", 1) and globals.timeout else "")
        title = "   " + title
        artist = "   " + artist
        self.title.setText(title)
        self.title.reset()
        self.artist.setText(artist)
        self.artist.reset()

    def update_style(self, ground=None, accent=None):
        if ground:
            ground = '#%02x%02x%02x' % ground[0]
        if accent:
            accent = '#%02x%02x%02x' % accent[0]
        self.title.setColor(accent if accent else "#868686")
        self.artist.setColor(accent if accent else "#868686")
        globals.app.setStyleSheet("""
#main {
    background: """ + (ground if ground else "#1E1E1E") + """;
    border-radius: 5px
}

#fade_left {
    background: qlineargradient(x1:0, y1:0, x2:0.071, y2:0, stop:0 #FF""" + (ground if ground else "#1E1E1E")[1:] + """, stop:1 #00""" + (ground if ground else "#1E1E1E")[1:] + """);
    margin-bottom: 4px
}

#fade_right {
    background: qlineargradient(x1:0.89, y1:0, x2:0.99, y2:0, stop:0 #00""" + (ground if ground else "#1E1E1E")[1:] + """, stop:1 #FF""" + (ground if ground else "#1E1E1E")[1:] + """);
    margin-bottom: 4px;
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

QMenu::item {
    padding: 2px 10px 2px 5px
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1276EF, stop:1 #BA31EF);
    color: rgb(255, 255, 255)
}

#SoundySettings {
    background: """ + (ground if ground else "#1E1E1E") + """
}

QCheckBox {
    color: """ + (accent if accent else "#868686") + """
}

QCheckBox::indicator {
    border: 2px solid """ + (accent if accent else "#868686") + """;
    border-radius: 6px;
    background: """ + (ground if ground else "#1E1E1E") + """;
    width: 16px;
    height: 16px
}

QCheckBox::indicator:checked {
    border-color: """ + (accent if accent else "#868686") + """;
    background: """ + (accent if accent else "#868686") + """;
    image: url(resources/icons/check.png)
}
""")


class SoundyTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        self.icon = QIcon('resources/icons/icon.png')
        QSystemTrayIcon.__init__(self, self.icon, parent)

        # Context menu
        self.menu = QMenu(parent)

        # Watermark item
        self.watermark = QAction(f"Soundy v{globals.version}")
        self.watermark.setEnabled(False)
        self.menu.addAction(self.watermark)

        # Releases item
        self.releases = QAction("See new updates")
        self.releases.triggered.connect(lambda e=None: webbrowser.open('https://github.com/Willy-JL/soundy/releases', new=2))
        self.menu.addAction(self.releases)

        # Settings item
        self.settings = QAction("Settings")
        self.settings.triggered.connect(lambda e=None: globals.settings_gui.show())
        self.menu.addAction(self.settings)

        # Exit item
        self.exit = QAction("Exit")
        self.exit.triggered.connect(lambda e=None: globals.gui.close())
        self.menu.addAction(self.exit)

        # Apply context menu
        self.setContextMenu(self.menu)


class SoundySettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('resources/icons/icon.png'))

        if not self.objectName():
            self.setObjectName(u"SoundySettings")
        self.setFixedSize(0, 0)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)

        self.layout = QGridLayout(self)
        self.layout.setObjectName(u"layout")
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(15)


        self.always_on_top = QCheckBox(self)
        self.always_on_top.setObjectName(u"always_on_top")
        self.always_on_top.setFont(globals.font_artist)
        self.always_on_top.setText(" Always on top (requires app restart)")

        self.layout.addWidget(self.always_on_top, 0, 0, 1, 1, Qt.AlignLeft)

        self.auto_hide = QCheckBox(self)
        self.auto_hide.setObjectName(u"auto_hide")
        self.auto_hide.setFont(globals.font_artist)
        self.auto_hide.setText(" Auto hide when no media is detected")

        self.layout.addWidget(self.auto_hide, 1, 0, 1, 1, Qt.AlignLeft)

        self.discord_rpc = QCheckBox(self)
        self.discord_rpc.setObjectName(u"discord_rpc")
        self.discord_rpc.setFont(globals.font_artist)
        self.discord_rpc.setText(" Discord Rich Presence integration")

        self.layout.addWidget(self.discord_rpc, 2, 0, 1, 1, Qt.AlignLeft)

        self.run_at_startup = QCheckBox(self)
        self.run_at_startup.setObjectName(u"run_at_startup")
        self.run_at_startup.setFont(globals.font_artist)
        self.run_at_startup.setText(" Run Soundy at Windows startup")

        self.layout.addWidget(self.run_at_startup, 3, 0, 1, 1, Qt.AlignLeft)

        self.scrolling_text = QCheckBox(self)
        self.scrolling_text.setObjectName(u"scrolling_text")
        self.scrolling_text.setFont(globals.font_artist)
        self.scrolling_text.setText(" Allow scrolling text for long names")

        self.layout.addWidget(self.scrolling_text, 4, 0, 1, 1, Qt.AlignLeft)


        QMetaObject.connectSlotsByName(self)

        self.setWindowTitle(f"Soundy Settings")

    def showEvent(self, event):
        try:
            self.always_on_top.stateChanged.disconnect()
        except TypeError:
            pass
        self.always_on_top.setChecked(bool(globals.settings.value("alwaysOnTop", 1)))
        self.always_on_top.stateChanged.connect(self.set_always_on_top)

        try:
            self.auto_hide.stateChanged.disconnect()
        except TypeError:
            pass
        self.auto_hide.setChecked(bool(globals.settings.value("autoHide", 1)))
        self.auto_hide.stateChanged.connect(self.set_auto_hide)

        try:
            self.discord_rpc.stateChanged.disconnect()
        except TypeError:
            pass
        self.discord_rpc.setChecked(bool(globals.settings.value("discordRPC", 0)))
        self.discord_rpc.stateChanged.connect(self.set_discord_rpc)

        try:
            self.run_at_startup.stateChanged.disconnect()
        except TypeError:
            pass
        self.run_at_startup.setChecked(QSettings("HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", QSettings.NativeFormat).value("Soundy", "") == f'"{sys.executable}"')
        self.run_at_startup.stateChanged.connect(self.set_run_at_startup)

        try:
            self.scrolling_text.stateChanged.disconnect()
        except TypeError:
            pass
        self.scrolling_text.setChecked(bool(globals.settings.value("scrollingText", 1)))
        self.scrolling_text.stateChanged.connect(self.set_scrolling_text)

        event.accept()

    def set_always_on_top(self, *args):
        globals.settings.setValue("alwaysOnTop", int(self.always_on_top.isChecked()))

    def set_auto_hide(self, *args):
        globals.settings.setValue("autoHide", int(self.auto_hide.isChecked()))
        globals.timeout = None

    def set_discord_rpc(self, *args):
        globals.settings.setValue("discordRPC", int(self.discord_rpc.isChecked()))
        if self.discord_rpc.isChecked():
            globals.discord_rpc.initialize('826397574394413076', callbacks={}, log=False)
        else:
            globals.discord_rpc.shutdown()

    def set_run_at_startup(self, *args):
        startup_settings = QSettings("HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", QSettings.NativeFormat)
        if self.run_at_startup.isChecked():
            startup_settings.setValue("Soundy", f'"{sys.executable}"')
        else:
            startup_settings.setValue("Soundy", "")

    def set_scrolling_text(self, *args):
        globals.settings.setValue("scrollingText", int(self.scrolling_text.isChecked()))
        globals.gui.title.reset()
        globals.gui.artist.reset()


async def label_loop():
    while True:
        if globals.settings.value("scrollingText", 1):
            title_task = globals.loop.create_task(globals.gui.title.marquee())
            artist_task = globals.loop.create_task(globals.gui.title.marquee())
            while not title_task.done() and not artist_task.done():
                await asyncio.sleep(1)
        await asyncio.sleep(6)
