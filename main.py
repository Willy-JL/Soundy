from PyQt5 import QtWidgets, QtGui
from qasync import QEventLoop
import asyncio
import sys

from modules import callbacks, globals, gui, singleton


try:
    globals.singleton = singleton.Singleton("Soundy")
except RuntimeError:
    sys.exit()


if __name__ == '__main__':

    # Create App
    globals.app = QtWidgets.QApplication(sys.argv)
    # globals.app.setQuitOnLastWindowClosed(False)

    # Configure asyncio loop to work with PyQt
    loop = QEventLoop(globals.app)
    asyncio.set_event_loop(loop)
    globals.loop = asyncio.get_event_loop()

    # Setup fonts
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/materialdesignicons-webfont.ttf")
    globals.font_mdi = QtGui.QFont('Material Design Icons', 26)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Medium.ttf")
    globals.font_track = QtGui.QFont('Poppins Medium', 13, 400)
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Poppins-Light.ttf")
    globals.font_artist = QtGui.QFont('Poppins Light', 10, 300)

    # Setup GUIs
    globals.gui = gui.SoundyGUI()

    # Finally show GUI
    globals.gui.show()

    globals.loop.create_task(callbacks.update_loop())

    # Set off loop
    with globals.loop:
        sys.exit(globals.loop.run_forever())
