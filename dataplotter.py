# -*- coding: utf-8 -*-

from PyQt4 import QtCore

from data_tools import ZoneDict, MEFPiePlotZoneHeatNeed, AFFPiePlotZoneHeatNeed, Init_Table_check

class DataPlotter(object):
    """Virtual class

       Useless by itself. Implement in sub-clases
    """
    
    def __init__(self, color_chart):
        
        # Get color chart
        self._color_chart = color_chart

class ConsPerZonePieDataPlotter(DataPlotter):

    def __init__(self, Con_Zon_Pie_Trace_Butt, MplWidget, TableWidget, 
        data_reader, color_chart):
        
        super(ConsPerZonePieDataPlotter, self).__init__(color_chart)
        
        self._zdico={}
        self._aff_zone_val=[]
        self._aff_zone_nom=[]
        self._aff_zone_nuanc=[]
        self._data_reader = data_reader
        self._list_data = None
        self._init=True
        
        self._Con_Zon_Pie_Trace_Butt=Con_Zon_Pie_Trace_Butt #Acquisition du boutton pour tracer
        self._MplWidget=MplWidget #Aquisition du Widget graphe
        self._TableWidget=TableWidget #Acquisition du widget tableau
        
        # Tab Conso Zone Pie
        # Commande du bouton de chargement
        self._Con_Zon_Pie_Trace_Butt.clicked.connect(self.trace_button_cbk) 

    def trace_button_cbk(self):
        
        self._list_data = self._data_reader.list_dat

        if self._init == True:          
            self._zdico = ZoneDict(self._list_data)
            
            self._aff_zone_val, self._aff_zone_nom, self._aff_zone_nuanc = MEFPiePlotZoneHeatNeed(self._zdico, self._color_chart)
            AFFPiePlotZoneHeatNeed(self._aff_zone_val, self._aff_zone_nom, self._aff_zone_nuanc, self._MplWidget)
            
            Init_Table_check(self._aff_zone_val, self._aff_zone_nom, self._TableWidget)
            self._init = False

        else :
            self._list_zone = []
            for i in range(len(self._zdico)):
                if self._TableWidget.item(i,0).checkState() == QtCore.Qt.Checked:
                    self._list_zone.append(self._zdico[str(self._TableWidget.item(i,0).text())]['Zone Total Internal Total Heating Rate'])
                    
            self._list_zone = ZoneDict(self._list_zone)
            
            self._aff_zone_val, self._aff_zone_nom, self._aff_zone_nuanc = MEFPiePlotZoneHeatNeed(self._list_zone, self._color_chart)
            AFFPiePlotZoneHeatNeed(self._aff_zone_val,self._aff_zone_nom,self._aff_zone_nuanc,self._MplWidget)

