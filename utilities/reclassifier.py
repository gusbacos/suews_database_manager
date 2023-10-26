import pandas as pd
import numpy as np
import webbrowser
from pathlib import Path

from qgis.PyQt.QtCore import  QVariant
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import QgsVectorLayer, QgsMapLayerProxyModel, QgsFeature, QgsProject, QgsField, QgsVectorFileWriter

def setup_reclassifier(self, dlg, db_dict):

    def fill_cbox(dlg):        
        typology_list = list(db_dict['NonVeg'].loc[db_dict['NonVeg']['Surface'] == 'Buildings', 'descOrigin'])

        for i in range(1,23):
            Nc = eval('dlg.comboBoxNew' + str(i))
            Nc.addItems(typology_list)
            Nc.setCurrentIndex(-1)
            Nc.setDisabled(True)
            vars()['dlg.comboBoxNew' + str(i)] = Nc
        
        dlg.comboBoxType.clear()
        dlg.comboBoxType.addItems(typology_list)
        dlg.comboBoxType.setCurrentIndex(-1)

    def field_changed():

        layer = self.layerComboManagerPoint.currentLayer()

        att_list = []
        for fieldName in layer.fields():
            att_list.append(fieldName.name())
        att_column = dlg.comboBoxField.currentText()
        if att_column != '':
            att_index = att_list.index(att_column)
            
            unique_values = list(layer.uniqueValues(att_index))
            len_uv = len(unique_values)

            # Ensure always String 
            unique_values = ([str(x) for x in unique_values])

            for i in range(1,23):
                # Oc == Old Class
                Oc = eval('dlg.comboBoxClass' + str(i))
                Oc.clear()
                Oc.setDisabled(True)
                vars()['dlg.comboBoxClass' + str(i)] = Oc
                # Nc == New Class
                Nc = eval('dlg.comboBoxNew' + str(i))
                Nc.setCurrentIndex(-1)
                Nc.setDisabled(True)
                vars()['dlg.comboBoxNew' + str(i)] = Nc
            
            # Add Items to left side Comboboxes and enable right side comboboxes 
            for i in range(len_uv):
                idx = i+1
                if idx > 22:
                    break 
                Oc = eval('dlg.comboBoxClass' + str(idx))
                Oc.addItems(unique_values)
                Oc.setCurrentIndex(i)
                vars()['dlg.comboBoxClass' + str(idx)] = Oc

                Nc = eval('dlg.comboBoxNew' + str(idx))
                Nc.setEnabled(True)
                vars()['dlg.comboBoxNew' + str(idx)] = Nc

    def layer_changed():

        try:
            layer = self.layerComboManagerPoint.currentLayer()
            att_list = list(layer.attributeAliases())
            dlg.comboBoxField.clear()
            dlg.comboBoxField.setEnabled(True)
            dlg.comboBoxField.addItems(att_list)
            dlg.comboBoxField.setCurrentIndex(0)

            field_changed() 
        except:
            pass
        
    def typology_info():
        typology_str = dlg.comboBoxType.currentText()
        dlg.textBrowser.clear()
        if dlg.comboBoxType.currentIndex() != -1:
            typology_sel = db_dict['NonVeg'].loc[db_dict['NonVeg']['descOrigin'] == typology_str]
            
            name = typology_sel['Description'].item()
            origin  = typology_sel['Origin'].item()

            dlg.textBrowser.setText(
                'Typology:' + name + '\n' +
                'Origin: ' + origin + '\n' + 
                'More....'
                )
        
    def savefile():
        # Add possibilites to save as other format? Is .shp only format used in SUEWS Prepare?
        self.outputfile = self.fileDialog.getSaveFileName(None, 'Save File As:', None, 'Shapefiles (*.shp)')
        dlg.textOutput.setText(self.outputfile[0])

    def start_progress():

        vlayer = self.layerComboManagerPoint.currentLayer()
        att_list = []

        QgsVectorFileWriter.writeAsVectorFormat(vlayer, dlg.textOutput.text(), "UTF-8", vlayer.crs(), "ESRI Shapefile")
        vlayer = QgsVectorLayer(self.outputfile[0], Path(self.outputfile[0]).name[:-4])

        for fieldName in vlayer.fields():
            att_list.append(fieldName.name())

        att_column = dlg.comboBoxField.currentText() # Selected columns in  vectorlayer
        att_index = att_list.index(att_column)
        
        unique_values = list(vlayer.uniqueValues(att_index))
        
        dict_reclass = {}       # dict for reclassifying typologynames as string
        dict_reclassID = {}     # dict for reclassifying typologyID as integer

        idx = 1
        for i in range(len(unique_values)): #FIX CORRECT
        
            if idx > 13:
                break 
            # Left side
            Oc = eval('dlg.comboBoxClass' + str(idx))
            oldField = Oc.currentText()
            
            # Right Side
            Nc = eval('dlg.comboBoxNew' + str(idx))
            newField = Nc.currentText()                
            dict_reclass[str(oldField)] = str(newField) 
            dict_reclassID[str(oldField)] = db_dict['NonVeg'].loc[db_dict['NonVeg']['descOrigin'] == str(newField)].index.item()
            idx += 1

        newFieldName = 'TypologyNA' # New field for typology name
        newFieldID = 'TypologyID'   # New field for typologyID

        # Add fields in vectorlayer
        fields = [
            QgsField(newFieldName, QVariant.String),
            QgsField(newFieldID, QVariant.Int),
        ]

        vlayer.startEditing()
        vlayer.dataProvider().addAttributes(fields)
        vlayer.updateFields()
        
        # Reclassify new fields using reclassify dictionaries created above
        for feature in vlayer.getFeatures():
            old_value = feature[att_column] 
            new_value1 = dict_reclass.get(old_value, None)
            new_value2 = dict_reclassID.get(old_value, None)
            
            if new_value1 is not None:
                feature[newFieldName] = new_value1
            if new_value2 is not None:
                feature[newFieldID] = new_value2
            
            vlayer.updateFeature(feature)

        vlayer.commitChanges()

        QgsProject.instance().addMapLayer(vlayer) # Add vectorlayer to QGIS-project

        QMessageBox.information(None, 'Process Complete', 'Your reclassified shapefile has been added to project. Proceed to SUEWS-Preprare')
        dlg.textOutput.clear()

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 0:
            fill_cbox(dlg)
    
    def to_type_edit():
        self.dlg.tabWidget.setCurrentIndex(1)

    self.layerComboManagerPoint = dlg.comboBoxVector
    self.layerComboManagerPoint.setCurrentIndex(-1)
    self.layerComboManagerPoint.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    # fill_cbox()
    dlg.editTypeButton.clicked.connect(to_type_edit)

    dlg.comboBoxVector.currentIndexChanged.connect(layer_changed)
    dlg.comboBoxField.currentIndexChanged.connect(field_changed)

    self.fileDialog = QFileDialog()
    dlg.pushButtonSave.clicked.connect(savefile)
    
    # Set up for the run button
    dlg.runButton.clicked.connect(start_progress)

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 0:
            fill_cbox(dlg)
    
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    dlg.comboBoxType.currentIndexChanged.connect(typology_info)

        
