from modules import globals
globals.version = "2.0"

import sys

class Logger(object):
    def __init__(self):
        self.console = sys.stdout

    def write(self, message):
        self.console.write(message)
        with open("Soundy.log", "a") as log:
            log.write(message)

    def flush(self):
        self.console.flush()

sys.stdout = Logger()
sys.stderr = sys.stdout

import datetime
current = datetime.datetime.now()
print(f'Soundy v{globals.version} starting at {"0" if current.day < 10 else ""}{current.day}/{"0" if current.month < 10 else ""}{current.month}/{current.year} - {"0" if current.hour < 10 else ""}{current.hour}:{"0" if current.minute < 10 else ""}{current.minute}:{"0" if current.second < 10 else ""}{current.second}')


from PyQt5 import QtWidgets, QtGui, QtCore
from qasync import QEventLoop
import discord_rpc
import asyncio

from modules import gui, listener, singleton
globals.discord_rpc = discord_rpc


try:
    globals.singleton = singleton.Singleton("Soundy")
except RuntimeError:
    sys.exit()


if __name__ == '__main__':

    # Create App
    globals.app = QtWidgets.QApplication(sys.argv)
    globals.app.setQuitOnLastWindowClosed(False)

    # Configure asyncio loop to work with PyQt
    globals.loop = QEventLoop(globals.app)
    asyncio.set_event_loop(globals.loop)

    # Setup fonts
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/materialdesignicons-webfont.ttf")
    globals.font_mdi_38 = QtGui.QFont('Material Design Icons', 38)
    globals.font_mdi_26 = QtGui.QFont('Material Design Icons', 26)
    globals.font_mdi_18 = QtGui.QFont('Material Design Icons', 18)
    globals.font_mdi_13 = QtGui.QFont('Material Design Icons', 13)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Medium.ttf")
    globals.font_track = QtGui.QFont('Poppins Medium', 13, 400)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Light.ttf")
    globals.font_artist = QtGui.QFont('Poppins Light', 10, 300)

    # Setup GUI components
    globals.settings = QtCore.QSettings("WillyJL", "Soundy")
    globals.settings_gui = gui.SoundySettings()
    globals.gui = gui.SoundyGUI()
    globals.tray = gui.SoundyTray(globals.gui)

    # Finally show GUIs
    globals.tray.show()
    globals.gui.show()

    # Initialize discord rpc
    if globals.settings.value("discordRPC", 0):
        globals.discord_rpc.initialize('826397574394413076', callbacks={}, log=True)

    # Start main listener loop
    globals.loop.create_task(listener.listener_loop())

    # Set off loop
    with globals.loop:
        sys.exit(globals.loop.run_forever())
