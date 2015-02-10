#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal

from PyQt4 import QtGui, QtCore, uic

from data_tools import Analyse_Simu, Tab_Conso_Zone_Pie

class SimuPlot(QtGui.QMainWindow):
    
    def __init__(self):
        
        super(SimuPlot, self).__init__()

        # UI
        ui = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
        self._ui = uic.loadUi(ui, self)
        
        # Création des instances de classe
        # Création de l'instance principale ET de lecture du fichier
        self.Simu = Analyse_Simu(self._ui.Info_Load,
                                 self._ui.File_Path_Text,
                                 self._ui.progressBar) 
        # Création de l'instance Tab consommation zones Pie
        self.Ctab_Con_Zon_Pie = Tab_Conso_Zone_Pie( \
            self._ui.Con_Zon_Pie_Trace_Butt,
            self._ui.MplWidget,
            self._ui.table_Con_Zon) 

        # Tab Fichier
        # Commande du bouton de recherche(browse)
        self.Load_Button.clicked.connect(self.Simu.Browse_Button) 
        # Commande du bouton de chargement
        self.Ok_Load_Button.clicked.connect(self.Simu.Lect_File) 
        # Tab Conso Zone Pie
        # Commande du bouton de chargement
        self.Con_Zon_Pie_Trace_Butt.clicked.connect(self.Ctab_Con_Zon_Pie.Trace_Button) 

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    
    # Let the interpreter run each 100 ms to catch SIGINT.
    signal.signal(signal.SIGINT, lambda *args : QApplication.quit())
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)  
    
    mySW = SimuPlot()
    mySW.show()
    
    sys.exit(app.exec_())

