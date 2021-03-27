from PyQt5 import QtWidgets, QtGui
from qasync import QEventLoop
import asyncio
import sys

from modules import api, globals, gui, interactions, singleton


try:
    globals.singleton = singleton.Singleton("Soundy")
except RuntimeError:
    sys.exit()


if __name__ == '__main__':

    # Create App
    globals.app = QtWidgets.QApplication(sys.argv)
    globals.app.setQuitOnLastWindowClosed(False)

    # Configure asyncio loop to work with PyQt
    loop = QEventLoop(globals.app)
    asyncio.set_event_loop(loop)
    globals.loop = asyncio.get_event_loop()

    # Setup font awesome for icons
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Font Awesome 5 Free-Solid-900.otf")
    globals.font_awesome = QtGui.QFont('Font Awesome 5 Free Solid', 16)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Medium.ttf")
    globals.font_track = QtGui.QFont('Poppins Medium', 13, 400)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Light.ttf")
    globals.font_artist = QtGui.QFont('Poppins Light', 10, 300)

    # Setup GUIs
    globals.gui = gui.SoundyGUI()
    globals.app.setStyleSheet(gui.QSS)

    # Finally show GUI
    globals.gui.show()

    globals.loop.create_task(interactions.update_loop())

    # Set off loop
    with globals.loop:
        sys.exit(globals.loop.run_forever())
