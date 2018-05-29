import sys
import signal

from PyQt5 import QtCore, QtGui, QtWidgets

from .mainwindow import MainWindow, __version__  # noqa
from .paths import I18N_PATH


def main():

    app = QtWidgets.QApplication(sys.argv)

    # Internationalization
    # Use system locale
    locale = QtCore.QLocale.system().name()
    # Load default translator for Qt strings
    translator_qt = QtCore.QTranslator()
    translator_qt.load('qt_{}'.format(locale),
        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(translator_qt)
    # Load translator for own strings
    translator = QtCore.QTranslator()
    translator.load(str(I18N_PATH / ('simuplot_' + locale)))
    app.installTranslator(translator)

    # Let the interpreter run each 100 ms to catch SIGINT.
    signal.signal(signal.SIGINT, lambda *args : app.quit())
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    mySW = MainWindow(app)
    mySW.show()

    sys.exit(app.exec_())
