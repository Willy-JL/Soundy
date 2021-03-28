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

    # Setup GUIs
    globals.gui = gui.SoundyGUI()

    # Finally show GUI
    globals.gui.show()

    globals.loop.create_task(callbacks.update_loop())

    # Set off loop
    with globals.loop:
        sys.exit(globals.loop.run_forever())
