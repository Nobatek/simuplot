# -*- coding: utf-8 -*-

import csv
from math import *      #importe la fonction numpy
import numpy as np
import matplotlib
from pylab import *
from scipy.stats import norm
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QFileDialog




#-------------------------------------------------------------------------------------
#Objet Donnee
#-------------------------------------------------------------------------------------
class Data(object):
    def __init__(self,Zone="none",DataID="none",Unit="-",Type="none",Vals=array([])):
        self._Zone=Zone
        self._DataID=DataID
        self._Unit=Unit
        self._Type=Type
        self._Vals=Vals

    def Zone(self):
        return self._Zone

    def DataID(self):
        return self._DataID

    def Unit(self):
        return self._Unit

    def Type(self):
        return self._Type

    def Vals(self):
        return self._Vals

    def NBvals(self):
        return len(self._Vals)

#-------------------------------------------------------------------------------------
#Fonction pour affichage des caractères spéciaux
#-------------------------------------------------------------------------------------
def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


#-------------------------------------------------------------------------------------
#Classer un dictionnaire par valeur retourne les valeur et la liste items
#-------------------------------------------------------------------------------------
def sort_by_value(d):
    """ Returns the keys of dictionary d sorted by their values """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))],[ backitems[i][0] for i in range(0,len(backitems))]
    #return Keys,Items

#-------------------------------------------------------------------------------------
#Fonction LectDon
#-------------------------------------------------------------------------------------
def LectDat(FilePath,ProgressBar):
    
    #Recuperation donnees sortie
    Vals=list()
    try:
        csv_file = open(FilePath, "rb")
    except IOError:
        return "Chemin d'accès au fichier incorrecte"
    except UnicodeDecodeError:
        return "Presence de caracteres non autorises"
        
    Myreader = csv.reader(csv_file,delimiter=",")
    
    #Acquisition des donne brutes
    NomDonnee=next(Myreader)

    for row in Myreader:
        Vals.append(row)


    #Traitement des attributs + gestion des erreur fichiers
    try:
        NomDonnee.remove('Date/Time') #supression des dates/heures
    except ValueError :
        return "Type de fichier non compatible\n\n - Selectioner un fichier Energy Plus"

    #Identification des zones
    ZoneID=[[NomDonnee[k][0:i] for i in range(len(NomDonnee[k])) if NomDonnee[k][i]==':'] for k in range(len(NomDonnee))] #Identification des zones par rapport au ':'
    ZoneID=[ZoneID[i][0] for i in range(len(ZoneID))]
    ProgressBar.setProperty("value", 16)

    #Identification du type de sortie
    DataID=[[NomDonnee[k][0:i-1] for i in range(len(NomDonnee[k])) if NomDonnee[k][i]=='['] for k in range(len(NomDonnee))] #Identification borne superieure (-1 pour l'espace)
    DataID=[DataID[i][0] for i in range(len(DataID))]
    DataID=[[DataID[k][i+1::] for i in range(len(DataID[k])) if DataID[k][i]==':'] for k in range(len(DataID))] #Identification borne superieure (+1 pour virer les ':')
    DataID=[DataID[i][0] for i in range(len(DataID))]
    ProgressBar.setProperty("value", 32)

    #Identification des unitees
    UnitID=[[NomDonnee[k][0:i] for i in range(len(NomDonnee[k])) if NomDonnee[k][i]==']'] for k in range(len(NomDonnee))]  #Identification borne superieure
    UnitID=[UnitID[i][0] for i in range(len(UnitID))]
    UnitID=[[UnitID[k][i+1::] for i in range(len(UnitID[k])) if UnitID[k][i]=='['] for k in range(len(UnitID))] #Identification borne superieure (+1 pour virer les '[')
    UnitID=[UnitID[i][0] for i in range(len(UnitID))]
    ProgressBar.setProperty("value", 48)

    #Identification du type
    TypeID=[[NomDonnee[k][0:i] for i in range(len(NomDonnee[k])) if NomDonnee[k][i]==')'] for k in range(len(NomDonnee))]
    TypeID=[TypeID[i][0] for i in range(len(TypeID))]
    TypeID=[[TypeID[k][i+1::] for i in range(len(TypeID[k])) if TypeID[k][i]=='('] for k in range(len(TypeID))]
    TypeID=[TypeID[i][0] for i in range(len(TypeID))]
    ProgressBar.setProperty("value", 64)

    #Traitement des donnees
    Vals=[[Vals[k][i] for i in range(1,len(Vals[k]))] for k in range(len(Vals))] #supressions des dates/heures
    Vals=[map(float,Vals[i]) for i in range(len(Vals))] #Conversion des donnees en nombre
    Vals=array(Vals)
    ProgressBar.setProperty("value", 80)
    
    #Creation de ListDat
    try:
        ListDat=[Data(ZoneID[i],DataID[i],UnitID[i],TypeID[i],Vals[:,i]) for i in range(len(ZoneID))]
    except IndexError :
        return "Fichier EnergyPlus non conforme\n\n - Verifier qu'il n'y a pas de sortie annuel (DISTRICT)\n - Verifier que toutes les variables sont de type (HOURLY)"
        
    ProgressBar.setProperty("value", 100)
    
    return ListDat

#-------------------------------------------------------------------------------------
#Fonction ZoneDict : Organise les donnees par zone
#-------------------------------------------------------------------------------------
def ZoneDict(ListDat):
    
    #creation de la liste de zone
    ZoneList=[ListDat[i].Zone() for i in range(len(ListDat))]
    ZoneList=list(set(ZoneList))
    ZDico={ZoneList[i]:{ListDat[k].DataID(): ListDat[k] for k in range(len(ListDat)) if ListDat[k].Zone()==ZoneList[i]} for i in range(len(ZoneList))} #affecte les Donnee dans le dictionnaire par zone
    
    return ZDico

#-------------------------------------------------------------------------------------
#Fonction MEFPiePlotZoneHeatNeed : Organise les donnees pour l creation du pie plot besoins de chauffage
#-------------------------------------------------------------------------------------
def MEFPiePlotZoneHeatNeed(ZDico,Nuancier):
    ZoneList=ZDico.keys() #creation de la liste de zone
    ValList=[sum(list(ZDico[i]['Zone Total Internal Total Heating Rate'].Vals()))/1000 for i in ZoneList] #creation de la liste de valeurs correspondantes
    Dico={ZoneList[i]: ValList[i] for i in range(len(ZoneList))} #creation du dictionnaire associatif
    ZoneList,MEFData=sort_by_value(Dico) #convertsion en listes triees par valeur
    Nuanc=[Nuancier[i] for i in range(len(ZoneList))] #creation du nuancier

    return ZoneList,MEFData,Nuanc


#-------------------------------------------------------------------------------------
#Fonction AFFPiePlotZoneHeatNeed : Organise les donnees pour l creation du pie plot besoins de chauffage
#-------------------------------------------------------------------------------------
def AFFPiePlotZoneHeatNeed(ZoneList,MEFData,Nuanc,MplWidget):

    MplWidget.canvas.axes.cla()
    
    MplWidget.canvas.axes.pie(MEFData, labels=ZoneList, colors=Nuanc,
            autopct='%1.1f%%', shadow=False, startangle=90)
    MplWidget.canvas.axes.axis('equal')
    
    MplWidget.canvas.draw()
    

    return 0

#-------------------------------------------------------------------------------------
#Fonction Init_Table_check : Initialise un tableau avec des chekbox devant chaque liste
#-------------------------------------------------------------------------------------
def Init_Table_check(Stuff_list,Stuff_Val,QTableWidget):

    QTableWidget.setRowCount(len(Stuff_list))
    
    for i in range(len(Stuff_list)):
        item=QtGui.QTableWidgetItem(Stuff_list[i])
        item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                      QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)

        item2=QtGui.QTableWidgetItem(str(int(Stuff_Val[i])))
        
        QTableWidget.setItem(i, 0, item)
        QTableWidget.setItem(i, 1, item2)


#-------------------------------------------------------------------------------------
#Fonction Init_Table_check : Initialise un tableau avec des chekbox devant chaque liste
#-------------------------------------------------------------------------------------
def handleItemClicked(self, item):
    if item.checkState() == QtCore.Qt.Checked:
        print('"%s" Checked' % item.text())
    else:
        print('"%s" Clicked' % item.text())
        

#-------------------------------------------------------------------------------------
#class Analyse_Simu : Classe principale ET de lecture pour l'interaction avec Qt
#-------------------------------------------------------------------------------------
class Analyse_Simu(object):
    ListDat=[]      
    NuancNBK=['#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F',
                    '#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F','#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F']


    def __init__(self,Info_Load,File_Path_Text,progressBar):
        self._FilePath="none" #chemin d'accès du fichier à lire
        
        self._File_Path_Text=File_Path_Text #Acquisition de la zone de texte correspondant au chemin du fichier d'entree
        self._Info_Load=Info_Load #Acquisition de la zone label correspondant au information chargement
        self._progressBar=progressBar #Acquisition de la barre de chargement

    def Browse_Button(self):
        self._FilePath=QFileDialog.getOpenFileName() #activation du widget Browser
        self._File_Path_Text.setText(self._FilePath) #Mise a jour du chemin dans la zone de texte
        

    def Lect_File(self):
        Analyse_Simu.ListDat=[] #Reset des données à la lecture
        self._FilePath=self._File_Path_Text.text() #lis le chemin dans FilePath
        self._progressBar.setProperty("value", 0) #initialise la barre de chargement à 0
        Analyse_Simu.ListDat=LectDat(self._FilePath,self._progressBar) #Débute la fonction de lecture
        
        if type(Analyse_Simu.ListDat) is list :
            self._Info_Load.setText(_translate("Form","Fichier correctement charge ...", None))
        else :
            self._Info_Load.setText(_translate("Form",Analyse_Simu.ListDat, None))



#-------------------------------------------------------------------------------------
#class Tab_ConsoZone : Classe définissante les méthode de l'onglet Conso Pie
#-------------------------------------------------------------------------------------
class Tab_Conso_Zone_Pie(Analyse_Simu):
    def __init__(self,Con_Zon_Pie_Trace_Butt,MplWidget,TableWidget):
        self._zdico={}
        self._aff_zone_val=[]
        self._aff_zone_nom=[]
        self._aff_zone_nuanc=[]
        self._list_data=[]
        self._init=True
        
        self._Con_Zon_Pie_Trace_Butt=Con_Zon_Pie_Trace_Butt #Acquisition du boutton pour tracer
        self._MplWidget=MplWidget #Aquisition du Widget graphe
        self._TableWidget=TableWidget #Acquisition du widget tableau

        
    def Trace_Button(self):
        if self._init==True:          
            self._zdico=ZoneDict(Analyse_Simu.ListDat)
            self._aff_zone_val,self._aff_zone_nom,self._aff_zone_nuanc=MEFPiePlotZoneHeatNeed(self._zdico,Analyse_Simu.NuancNBK)
            AFFPiePlotZoneHeatNeed(self._aff_zone_val,self._aff_zone_nom,self._aff_zone_nuanc,self._MplWidget)
            Init_Table_check(self._aff_zone_val,self._aff_zone_nom,self._TableWidget)
            self._init=False

        else :
            self._list_zone=[]
            for i in range(len(self._zdico)):
                if self._TableWidget.item(i,0).checkState() == QtCore.Qt.Checked:
                    self._list_zone.append(self._zdico[str(self._TableWidget.item(i,0).text())]['Zone Total Internal Total Heating Rate'])
                    
            self._list_zone=ZoneDict(self._list_zone)
            self._aff_zone_val,self._aff_zone_nom,self._aff_zone_nuanc=MEFPiePlotZoneHeatNeed(self._list_zone,Analyse_Simu.NuancNBK)
            AFFPiePlotZoneHeatNeed(self._aff_zone_val,self._aff_zone_nom,self._aff_zone_nuanc,self._MplWidget)

            



        
        

    












        
    
