import pandas as pd
from .database_functions import save_to_db, create_code
from qgis.PyQt.QtWidgets import QMessageBox


#################################################################################################
#                                                                                               #
#                                  Antrhopogenic Emission Manager                               #
#                                                                                               #
#################################################################################################

def setup_anthropogenic_emission_manager(self, dlg, db_dict, db_path):
    
    def fill_cboxes():
        dlg.comboBoxBaseAnEm.addItems(db_dict['AnthropogenicEmission']['nameOrigin'].tolist())
        dlg.comboBoxBaseAnEm.setCurrentIndex(-1)
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)

        for i in range(1,18):
            Le = getattr(dlg, f'lineEdit_{i}')
            Le.clear()

        dlg.textEditName.clear()
        dlg.textEditOrig.clear()
        
    def base_AnEm_changed():

        base_irr = dlg.comboBoxBaseAnEm.currentText()
        AnEm_sel = db_dict['AnthropogenicEmission'][db_dict['AnthropogenicEmission']['nameOrigin'] == base_irr]

        AnEm_sel_dict = AnEm_sel.squeeze().to_dict()        
        for i in range(1,18):
            Tb = getattr(dlg, f'textBrowser_{i}')
            Le = getattr(dlg, f'lineEdit_{i}')
            Le.clear()
            Le.setText(str(AnEm_sel_dict[Tb.toPlainText()]))
    
    def model_changed():
        model = dlg.comboBoxModel.currentText()

        if model == str(2):
            for i in range(7,18):   
                Tb = getattr(dlg, f'textBrowser_{i}')
                Le = getattr(dlg, f'lineEdit_{i}')
                Tb.setDisabled(True)
                Le.setDisabled(True)
        elif model == str(4):
            for i in range(7,18):   
                Tb = getattr(dlg, f'textBrowser_{i}')
                Le = getattr(dlg, f'lineEdit_{i}')
                Tb.setEnabled(True)
                Le.setEnabled(True)
        else:
            pass       

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

    def add_AnEm():

        dict_reclass = {
            'ID' : create_code('AnthropogenicEmission'),
            'Name' : dlg.textEditName.value(),
            'Origin' : dlg.textEditOrig.value(),
        }
        
        for i in range(1,18):
            Tb = getattr(dlg, f'textBrowser_{i}')
            Le = getattr(dlg, f'lineEdit_{i}')
            col = Tb.toPlainText()
            val = Le.text()
            dict_reclass[col] = val
        
        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict['AnthropogenicEmission'] = pd.concat([db_dict['AnthropogenicEmission'], new_edit])

        save_to_db(db_path, db_dict)
        QMessageBox.information(None, 'Succesful', 'New edit added to your local database')
        fill_cboxes()


    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 4:
            fill_cboxes()

    def to_ref_edit():
        self.dlg.tabWidget.setCurrentIndex(10)

    dlg.pushButtonToRefManager.clicked.connect(to_ref_edit)
    dlg.pushButtonGen.clicked.connect(add_AnEm)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed)
    dlg.comboBoxBaseAnEm.currentIndexChanged.connect(base_AnEm_changed)
    dlg.comboBoxModel.currentIndexChanged.connect(model_changed)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    


    

