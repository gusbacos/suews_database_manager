import pandas as pd
from qgis.PyQt.QtWidgets import QMessageBox
from .database_functions import create_code, save_to_db

def setup_SS_material_creator(self, dlg, db_dict, db_path):

    def start_material_creator(dlg):

        dlg.comboBoxRef.clear()
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)
        dlg.textEditName.clear()
        dlg.textEditColor.clear()
        dlg.textEditOrig.clear()
        dlg.textEditAlbedo.clear()
        dlg.textEditEmissivity.clear()
        dlg.textEditThermalC.clear()
        dlg.textEditSpecificH.clear()

    def generate_material():

        dict_reclass = {
            'ID' : create_code('Spartacus Material'), 
            'Name' : str(dlg.textEditName.value()),
            'Color' : str(dlg.textEditColor.value()),
            'Origin': str(dlg.textEditOrig.value()),
            'Albedo': float((dlg.textEditAlbedo.value())),
            'Emissivity' : float((dlg.textEditEmissivity.value())),
            'Thermal Conductivity': float((dlg.textEditThermalC.value())),
            'Specific Heat': float((dlg.textEditSpecificH.value())),
            'Ref' : (db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() )
        }

        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict['Spartacus Material'] = pd.concat([db_dict['Spartacus Material'], new_edit])

        save_to_db(db_path, db_dict)

        QMessageBox.information(None, 'Succesful', 'New edit added to your local database')
        start_material_creator(dlg) # Clear tab

    def ref_changed():
        dlg.textBrowserRef.clear()
        try:
            ID = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item()
            dlg.textBrowserRef.setText(
                '<b>Author: ' +'</b>' + str(db_dict['References'].loc[ID, 'Author']) + '<br><br><b>' +
                'Year: ' + '</b> '+ str(db_dict['References'].loc[ID, 'Year']) + '<br><br><b>' +
                'Title: ' + '</b> ' +  str(db_dict['References'].loc[ID, 'Title']) + '<br><br><b>' +
                'Journal: ' + '</b>' + str(db_dict['References'].loc[ID, 'Journal']) + '<br><br><b>' +
                'DOI: ' + '</b>' + str(db_dict['References'].loc[ID, 'DOI']) + '<br><br><b>' 
            )
        except:
            pass

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 9:
            start_material_creator(dlg)

    def to_ref_edit():
        self.dlg.tabWidget.setCurrentIndex(10)
    
    dlg.pushButtonToRefManager.clicked.connect(to_ref_edit)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed)
    dlg.pushButtonGen.clicked.connect(generate_material)
