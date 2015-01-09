# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlotTool_GUI_V1.ui'
#
# Created: Wed Jan 07 16:14:24 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from Data_tools import * #importation de la classe principale

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PlotTool(object):
    def setupUi(self, PlotTool):
        PlotTool.setObjectName(_fromUtf8("PlotTool"))
        PlotTool.resize(1111, 730)
        self.gridLayout = QtGui.QGridLayout(PlotTool)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(PlotTool)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.Load_Tab = QtGui.QWidget()
        self.Load_Tab.setObjectName(_fromUtf8("Load_Tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.Load_Tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.Load_Button = QtGui.QCommandLinkButton(self.Load_Tab)
        self.Load_Button.setObjectName(_fromUtf8("Load_Button"))
        self.verticalLayout.addWidget(self.Load_Button)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.File_Path_Text = QtGui.QLineEdit(self.Load_Tab)
        self.File_Path_Text.setObjectName(_fromUtf8("File_Path_Text"))
        self.horizontalLayout.addWidget(self.File_Path_Text)
        self.Ok_Load_Button = QtGui.QPushButton(self.Load_Tab)
        self.Ok_Load_Button.setObjectName(_fromUtf8("Ok_Load_Button"))
        self.horizontalLayout.addWidget(self.Ok_Load_Button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(395, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.progressBar = QtGui.QProgressBar(self.Load_Tab)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.Info_Load = QtGui.QLabel(self.Load_Tab)
        self.Info_Load.setFrameShape(QtGui.QFrame.NoFrame)
        self.Info_Load.setFrameShadow(QtGui.QFrame.Plain)
        self.Info_Load.setObjectName(_fromUtf8("Info_Load"))
        self.verticalLayout.addWidget(self.Info_Load)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Load_Tab, _fromUtf8(""))
        self.Conso_Zone_Pie = QtGui.QWidget()
        self.Conso_Zone_Pie.setObjectName(_fromUtf8("Conso_Zone_Pie"))
        self.MplWidget = MplWidget(self.Conso_Zone_Pie)
        self.MplWidget.setGeometry(QtCore.QRect(454, 1, 621, 681))
        self.MplWidget.setObjectName(_fromUtf8("MplWidget"))
        self.Con_Zon_Pie_Trace_Butt = QtGui.QPushButton(self.Conso_Zone_Pie)
        self.Con_Zon_Pie_Trace_Butt.setGeometry(QtCore.QRect(170, 650, 75, 23))
        self.Con_Zon_Pie_Trace_Butt.setObjectName(_fromUtf8("Con_Zon_Pie_Trace_Butt"))
        
        self.table_Con_Zon = QtGui.QTableWidget(self.Conso_Zone_Pie)
        self.table_Con_Zon.setGeometry(QtCore.QRect(10, 30, 431, 291))
        self.table_Con_Zon.setObjectName(_fromUtf8("tableView"))
        
        self.tabWidget.addTab(self.Conso_Zone_Pie, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

 #Création des instances de classe
        self.Simu=Analyse_Simu(self.Info_Load,self.File_Path_Text,self.progressBar) #création de l'instance principale ET de lecture du fichier
        self.Ctab_Con_Zon_Pie=Tab_Conso_Zone_Pie(self.Con_Zon_Pie_Trace_Butt,self.MplWidget,self.table_Con_Zon) #création de l'instance Tab consommation zones Pie


        self.retranslateUi(PlotTool)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PlotTool)

    def retranslateUi(self, PlotTool):
        PlotTool.setWindowTitle(_translate("PlotTool", "PlotTool", None))
        self.Load_Button.setText(_translate("PlotTool", "Sélectionner le fichier à analyser", None))
        self.File_Path_Text.setText(_translate("PlotTool", "Spécifier un hemin d\'accès ...", None))
        self.Ok_Load_Button.setText(_translate("PlotTool", "Ok", None))
        self.Info_Load.setText(_translate("PlotTool", "En attente du chargement d\'un fichier résultats ...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Load_Tab), _translate("PlotTool", "Fichier", None))
        self.Con_Zon_Pie_Trace_Butt.setText(_translate("PlotTool", "Tracer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Conso_Zone_Pie), _translate("PlotTool", "Conso_Zones", None))

        #Tab Fichier
        self.Load_Button.clicked.connect(self.Simu.Browse_Button) # commande du bouton de recherche(browse)
        self.Ok_Load_Button.clicked.connect(self.Simu.Lect_File) # commande du bouton de chargement


        #Tab Conso Zone Pie
        self.Con_Zon_Pie_Trace_Butt.clicked.connect(self.Ctab_Con_Zon_Pie.Trace_Button) # commande du bouton de chargement
        




        
from mplwidget import MplWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PlotTool = QtGui.QWidget()
    ui = Ui_PlotTool()
    ui.setupUi(PlotTool)
    PlotTool.show()
    sys.exit(app.exec_())

