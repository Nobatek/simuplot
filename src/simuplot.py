#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal

# Forbid use of QString
# http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui, uic

from simuplot.mainwindow import MainWindow

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)

    # Let the interpreter run each 100 ms to catch SIGINT.
    signal.signal(signal.SIGINT, lambda *args : app.quit())
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)  

    mySW = MainWindow()
    mySW.show()

    sys.exit(app.exec_())

