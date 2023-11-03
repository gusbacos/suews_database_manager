import pandas as pd
from .database_functions import create_code, save_to_db
from qgis.PyQt.QtWidgets import QMessageBox

#################################################################################################
#                                                                                               #
#                                     Typology Editor                                           #
#                                                                                               #
#################################################################################################

def setup_urban_type_editor(self, dlg, db_dict, db_path):

    def fill_cbox():

        dlg.textEditOrig.clear()
        dlg.textEditDesc.clear()
        dlg.textEditName.clear()
        dlg.comboBoxTableSelect.clear()
        dlg.comboBoxTableSelect.addItems((db_dict['Types']['descOrigin'])) 
        dlg.comboBoxTableSelect.setCurrentIndex(-1)
        dlg.comboBoxPavedType.clear()
        dlg.comboBoxPavedType.addItems((db_dict['NonVeg']['descOrigin'][db_dict['NonVeg']['Surface'] == 'Paved']))
        dlg.comboBoxBuildingType.clear()
        dlg.comboBoxBuildingType.addItems((db_dict['NonVeg']['descOrigin'][db_dict['NonVeg']['Surface'] == 'Buildings']))
        for i in [dlg.comboBoxPavedType,dlg.comboBoxBuildingType]:
            i.setCurrentIndex(-1)
        dlg.comboBoxProf.setCurrentIndex(0)


    def check_type():
        if dlg.textEditName.isNull():
            QMessageBox.warning(None, 'Error in Name','Enter a name for new type')
        elif dlg.textEditName.value().startswith('test'):
            QMessageBox.warning(None, 'Error in Name','Please, don´t use test as type name..')
        elif dlg.textEditName.value().startswith('Test'):
            QMessageBox.warning(None, 'Error in Name','Please, don´t use test as type name..')
        elif dlg.textEditName.value() in db_dict['Types']['Type'].tolist():
            QMessageBox.warning(None, 'Error in Name','The suggested type name is already taken.')

        # Origin
        elif dlg.textEditOrig.isNull():
            QMessageBox.warning(None, 'Error in Origin','Enter a Origin for new type')
        # Final - When all is Checked 
        else:
            QMessageBox.information(None, 'Check Complete', 'Your type is compatible with the SUEWS-Database!\nPress Generate Type to add to your local Database')
            dlg.pushButtonGen.setEnabled(True)

    def changed(): 

        def type_changed(cbox, table, surface):
            urb_type = dlg.comboBoxTableSelect.currentText()
            if urb_type != '':
                indexer =db_dict['Types'][db_dict['Types']['descOrigin'] == urb_type][surface].item()
                table_indexer = table.loc[indexer,'descOrigin']
                cbox.setCurrentIndex(table['descOrigin'][table['Surface'] == surface].tolist().index(table_indexer))
        
        type_changed(dlg.comboBoxBuildingType, db_dict['NonVeg'],  'Buildings')
        type_changed(dlg.comboBoxPavedType, db_dict['NonVeg'], 'Paved')


    def generate_type():

        dict_reclass = {
            'ID' : create_code('Types'), #str('Type' + str(int(round(time.time())))),
            'Origin' : str(dlg.textEditOrig.value()),
            'Type' : str(dlg.textEditName.value()),
            'Description': dlg.textEditDesc.value(),
            'Profile Type' : dlg.comboBoxProf.currentText(),
            'Url' : '', 
            'Author' : 'SUEWS',
        }

        cbox_list = [dlg.comboBoxPavedType, dlg.comboBoxBuildingType]#, dlg.comboBoxGrassType, dlg.comboBoxDecType, dlg.comboBoxEvrType,dlg.comboBoxBsoilType, dlg.comboBoxWaterType]
        textbrowser_list = [dlg.textBrowser_0, dlg.textBrowser_1]#, dlg.textBrowser_2, dlg.textBrowser_3, dlg.textBrowser_4, dlg.textBrowser_5, dlg.textBrowser_6]
        
        for cbox, textbrowser in zip(cbox_list, textbrowser_list):

            var = textbrowser.toPlainText()
            surf_table = db_dict['NonVeg']
            dict_reclass[var] = surf_table[surf_table['descOrigin'] == cbox.currentText()].index.item()

        new_edit = pd.DataFrame.from_dict([dict_reclass]).set_index('ID')
        db_dict['Types'] = pd.concat([db_dict['Types'], new_edit])
    
        save_to_db(db_path, db_dict)
        fill_cbox()

        QMessageBox.information(None, 'Sucessful','Database Updated')

    def surface_info_changed(self):
        # TODO Update this. Outdated at the moment
        # Clear and enable ComboBox
        dlg.comboBoxElementInfo.clear()
        dlg.comboBoxElementInfo.setEnabled(True)
        # Read what surface user has chosen
        surface = dlg.comboBoxSurface.currentText()

        # Select correct tab fom DB (Veg, db_dict['NonVeg'] or Water)
        if surface == 'Paved' or surface == 'Buildings' or surface == 'Bare Soil':
            item_list = db_dict['NonVeg']['Description'][db_dict['NonVeg']['Surface'] == surface].tolist()
            origin = db_dict['NonVeg']['Origin'][db_dict['NonVeg']['Surface'] == surface].tolist()
            clr = db_dict['NonVeg']['Color'][db_dict['NonVeg']['Surface'] == surface].tolist()

            app_list = []
            for item, origin, clr in zip(item_list, origin, clr):
                # Join type and origin to present for user
                app_list.append((clr + ' ' + item + ', ' + origin))

        elif surface == 'Water':
            item_list = db_dict['NonVeg']['Description'][db_dict['NonVeg']['Surface'] == surface].tolist()
            origin = db_dict['NonVeg']['Origin'][db_dict['NonVeg']['Surface'] == surface].tolist()

            app_list = []
            for i, j in zip(item_list, origin):
                # Join type and origin to present for user
                app_list.append((i + ', ' + j))

        else: 
            item_list = db_dict['Veg']['Description'][db_dict['Veg']['Surface'] == surface].tolist()
            origin = db_dict['Veg']['Origin'][db_dict['Veg']['Surface'] == surface].tolist()

            app_list = []
            for i, j in zip(item_list, origin):
                # Join type and origin to present for user
                app_list.append((i + ', ' + j))

        dlg.comboBoxElementInfo.addItems(app_list)
    
    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 1:
            fill_cbox()
    
    def to_element_edit():
        self.dlg.tabWidget.setCurrentIndex(2)
    
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    dlg.comboBoxTableSelect.currentIndexChanged.connect(changed)
    dlg.comboBoxSurface.currentIndexChanged.connect(surface_info_changed)
    dlg.pushButtonCheck.clicked.connect(check_type)
    dlg.pushButtonGen.clicked.connect(generate_type)
    dlg.pushButtonEditElement.clicked.connect(to_element_edit)

