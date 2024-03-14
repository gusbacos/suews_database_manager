import pandas as pd
from .database_functions import save_to_db, create_code
from qgis.PyQt.QtWidgets import QMessageBox

#################################################################################################
#                                                                                               #
#                                  Irrigation manager                                           #
#                                                                                               #
#################################################################################################


def setup_irrigation_manager(self, dlg, db_dict, db_path):

    def fill_cboxes(dlg):
        dlg.comboBoxBaseIrr.clear()
        dlg.comboBoxRef.clear()
        dlg.textEditDesc.clear()
        dlg.textEditOrig.clear()
        
        for i in range(0,25):
            Le = eval('dlg.IrrLineEdit_' + str(i))
            Le.clear()
    
        dlg.comboBoxBaseIrr.addItems(db_dict['Irrigation']['descOrigin'].tolist())
        dlg.comboBoxBaseIrr.setCurrentIndex(-1)
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)

    def base_irr_changed():
        base_irr = dlg.comboBoxBaseIrr.currentText()
        irr_sel = db_dict['Irrigation'][db_dict['Irrigation']['descOrigin'] == base_irr]

        irr_sel_dict = irr_sel.squeeze().to_dict()

        for i in range(0,25):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.IrrLineEdit_' + str(i))
            Le.clear()
            Le.setText(str(irr_sel_dict[Tb.toPlainText()]))
    
    def ref_changed():
        dlg.textBrowserRef.clear()
        try:
            ID = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item()
            dlg.textBrowserRef.setText(
                '<b>Author: ' +'</b>' + str(db_dict['References'].loc[ID, 'Author']) + '<br><br><b>' +
                'Year: ' + '</b> '+ str(db_dict['References'].loc[ID, 'Publication Year']) + '<br><br><b>' +
                'Title: ' + '</b> ' +  str(db_dict['References'].loc[ID, 'Title']) + '<br><br><b>' +
                'Journal: ' + '</b>' + str(db_dict['References'].loc[ID, 'Journal']) + '<br><br><b>'
            )
        except:
            pass

    def add_irr():

        # refindex = db_dict['References'].copy()
        # refindex['authorYear'] = (refindex['Author'] + ' ,(' + refindex['Publication Year'].apply(str) + ')')
        dict_reclass = {
            'ID' : create_code('Irrigation'),
            'Description' : dlg.textEditDesc.value(),
            'Origin' : dlg.textEditOrig.value(),
            'Ref' : db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        }

        for i in range(0, 25): 
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.IrrLineEdit_' + str(i))
            col = Tb.toPlainText()
            val = Le.text()
            dict_reclass[col] = val

        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict['Irrigation'] = pd.concat([db_dict['Irrigation'], new_edit])
        save_to_db(db_path, db_dict)

        QMessageBox.information(None, 'Succesful', 'Irrigation Entry added to your local database')

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 5:
            fill_cboxes(dlg)
    
    self.dlg.tabWidget.currentChanged.connect(tab_update)

    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed) 
    dlg.comboBoxBaseIrr.currentIndexChanged.connect(base_irr_changed)
    dlg.pushButtonGen.clicked.connect(add_irr)