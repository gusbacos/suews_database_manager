import pandas as pd
from .database_functions import save_to_db, create_code
from qgis.PyQt.QtWidgets import QMessageBox

#################################################################################################
#                                                                                               #
#                                  Profile creator (Profiles)                                   #
#                                                                                               #
#################################################################################################

def setup_profile_creator(self, dlg, db_dict, db_path):

    def fill_cbox():
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)
        dlg.comboBoxProfType.setCurrentIndex(-1)
        dlg.comboBoxDay.setCurrentIndex(-1)
        dlg.comboBoxBaseProfile.setCurrentIndex(1)
    
    def prof_type_changed():
        prof_type = dlg.comboBoxProfType.currentText()
        dlg.comboBoxBaseProfile.clear()

        prof_types = db_dict['Profiles']['descOrigin'][db_dict['Profiles']['Profile Type'] == prof_type]
        dlg.comboBoxBaseProfile.addItems(prof_types.tolist())
        dlg.comboBoxDay.setCurrentIndex(1)

    def day_changed():
        day = dlg.comboBoxDay.currentText()
        prof_type = dlg.comboBoxProfType.currentText()
        dlg.comboBoxBaseProfile.clear()

        prof_types_d = db_dict['Profiles'][db_dict['Profiles']['Profile Type'] == prof_type]
        prof_types_d = prof_types_d['descOrigin'][db_dict['Profiles']['Day'] == day]

        dlg.comboBoxBaseProfile.addItems(prof_types_d.tolist())
        dlg.comboBoxBaseProfile.setEnabled(True)

    def base_prof_changed():
        base_prof = dlg.comboBoxBaseProfile.currentText()
        prof_sel = db_dict['Profiles'][(db_dict['Profiles']['descOrigin'] == base_prof) & (db_dict['Profiles']['Day'] == dlg.comboBoxDay.currentText()) & (db_dict['Profiles']['Profile Type'] == dlg.comboBoxProfType.currentText())]
        prof_sel.columns = prof_sel.columns.map(str)
        prof_sel_dict = prof_sel.squeeze().to_dict()

        for i in range(0,24):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.lineEdit_' + str(i))
            Le.clear()
            Le.setText(str(prof_sel_dict[str(Tb.toPlainText())]))

    def ref_changed():
        dlg.textBrowserRef.clear()

        try:
            ID = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item()
            dlg.textBrowserRef.setText(
                '<b>Author: ' +'</b>' + str(db_dict['References'].loc[ID, 'Author']) + '<br><br><b>' +
                'Year: ' + '</b> '+ str(db_dict['References'].loc[ID, 'Year']) + '<br><br><b>' +
                'Title: ' + '</b> ' +  str(db_dict['References'].loc[ID, 'Title']) + '<br><br><b>' +
                'Journal: ' + '</b>' + str(db_dict['References'].loc[ID, 'Journal']) + '<br><br><b>'
            )
        except:
            pass
    def add_profile():

        dict_reclass = {
            'ID' : create_code('Profiles'),
            'General Type' : 'Reg',
            'Profile Type' : dlg.comboBoxProfType.currentText(), 
            'Day' : dlg.comboBoxDay.currentText(),
            'Description' : dlg.textEditDesc.value(),
            'Origin' : dlg.textEditOrig.value(),
            'Ref' : db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        }

        for i in range(0, 24): 
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.lineEdit_' + str(i))
            col = Tb.toPlainText()
            val = Le.text()
            dict_reclass[col] = val

        dict_reclass['Ref'] = db_dict[  'References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict['Profiles'] = pd.concat([db_dict['Profiles'], new_edit])
    
        # Write to db
        save_to_db(db_path, db_dict)

        QMessageBox.information(None, 'Succesful', 'Profile Entry added to your local database')
        fill_cbox()
    
    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 5:
            fill_cbox()

    def to_ref_edit():
        self.dlg.tabWidget.setCurrentIndex(10)
    

    dlg.pushButtonToRefManager.clicked.connect(to_ref_edit)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    dlg.pushButtonGen.clicked.connect(add_profile)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed) 
    dlg.comboBoxProfType.currentIndexChanged.connect(prof_type_changed)
    dlg.comboBoxBaseProfile.currentIndexChanged.connect(base_prof_changed)
    dlg.comboBoxDay.currentIndexChanged.connect(day_changed)
