#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import signal

# Forbid use of QString
# http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

from simuplot.mainwindow import MainWindow
from simuplot import I18N_PATH

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    # Internationalization
    # Specify codec for translation
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf-8"))
    # Use system locale
    locale = QtCore.QLocale.system().name()
    # Load default translator for Qt strings
    translator_qt = QtCore.QTranslator()
    translator_qt.load('qt_{}'.format(locale),
        QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(translator_qt)
    # Load translator for own strings
    translator = QtCore.QTranslator()
    translator.load(os.path.join(I18N_PATH, 'simuplot_' + locale))
    app.installTranslator(translator)

    # Let the interpreter run each 100 ms to catch SIGINT.
    signal.signal(signal.SIGINT, lambda *args : app.quit())
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    mySW = MainWindow(app)
    mySW.show()

    sys.exit(app.exec_())

