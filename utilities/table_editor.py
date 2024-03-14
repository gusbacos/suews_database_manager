import pandas as pd
from qgis.PyQt.QtWidgets import QMessageBox
from .database_functions import param_info_dict, create_code, save_to_db, surf_df_dict

#################################################################################################
#                                                                                               #
#                                        Table Editor                                           #
#                                                                                               #
#################################################################################################

def setup_table_editor(self, dlg, db_dict, db_path):

    def fill_cbox():
        dlg.comboBoxRef.clear()
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)

        dlg.comboBoxTableSelect.clear()
        dlg.comboBoxTableSelect.addItems(sorted(param_info_dict.keys()))
        dlg.comboBoxTableSelect.setCurrentIndex(-1)
    
        for i in range(0,15):
            Oc = eval('dlg.textBrowser_' + str(i))
            Oc.clear()
            Oc.setDisabled(True)
            Nc = eval('dlg.textEdit_Edit_' + str(i))
            Nc.clear()
            Nc.setDisabled(True)

    def table_changed():

        try:        
            dlg.comboBoxSeason.setDisabled(True)
            dlg.comboBoxSeason.setCurrentIndex(-1)
            dlg.textBrowserSeason.setDisabled(True)
            
            table_name = dlg.comboBoxTableSelect.currentText()
            dlg.textBrowserDf.clear()

            for i in range(0,15):
                Oc = eval('dlg.textBrowser_' + str(i))
                Oc.clear()
                Oc.setDisabled(True)
                Nc = eval('dlg.textEdit_Edit_' + str(i))
                Nc.clear()
                Nc.setDisabled(True)

                # Set surfaces that uses the selcted table
                dlg.comboBoxSurface.clear()

                dlg.comboBoxSurface.addItems(param_info_dict[table_name]['surface'])
                dlg.comboBoxSurface.setEnabled(True)
                dlg.comboBoxSurface.setCurrentIndex(0)   

                # Add correct parameters for selected table
                params = list(param_info_dict[table_name]['param'].keys())
            
                for idx in range(len(params)):
                    Oc = eval('dlg.textBrowser_' + str(idx))
                    Oc.setEnabled(True)
                    Oc.setText(str(params[idx]))
                    Oc.setToolTip(param_info_dict[table_name]['param'][params[idx]]['tooltip'])
                    Nc = eval('dlg.textEdit_Edit_' + str(idx))
                    Nc.setEnabled(True)

            if table_name == 'OHM':
                dlg.comboBoxSeason.setEnabled(True)
                dlg.comboBoxSeason.setCurrentIndex(0)
                dlg.textBrowserSeason.setEnabled(True)
        except:
            pass

    
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

    def add_table():

        table_name = dlg.comboBoxTableSelect.currentText()

        table = db_dict[table_name]
        columns_to_remove = ['General Type', 'Surface', 'Description','Origin','Ref','References', 'descOrigin']

        for remove in columns_to_remove:
            try:
                list(table).remove(remove)
            except:
                pass
        len_list = len(list(table))

        if table_name == 'Soil':
            dict_reclass = {
                'ID' : create_code['NonVeg'],
                'General Type' : 'NonVeg',
                'Surface' : 'NaN', 
                'Description' : dlg.textEditDesc.value(),
                'Origin' : dlg.textEditOrig.value()
            }
        else:
            dict_reclass = {
                'ID' : create_code(table_name),
                'General Type' : surf_df_dict[dlg.comboBoxSurface.currentText()],
                'Surface' : dlg.comboBoxSurface.currentText(), 
                'Description' : dlg.textEditDesc.value(),
                'Origin' : dlg.textEditOrig.value() 
            }
            if dlg.comboBoxTableSelect.currentText() == 'OHM':
                dict_reclass['Season'] = dlg.comboBoxSeason.currentText()
    
        for idx in range(len_list):
            # Left side
            Oc = eval('dlg.textBrowser_' + str(idx))
            if len(Oc.toPlainText()) <1:
                break
            oldField = Oc.toPlainText()
            # Right Side
            Nc = eval('dlg.textEdit_Edit_' + str(idx))
            newField = float(Nc.value())
            dict_reclass[oldField] =  newField

        dict_reclass['Ref'] = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict[table_name] = pd.concat([db_dict[table_name], new_edit])
    
        # Write to db
        save_to_db(db_path, db_dict)
       
        # self.setup_tabs()
        # self.dlg.tabWidget.setCurrentIndex(3)
        QMessageBox.information(None, 'Succesful', table_name + ' Entry added to your local database')

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 2:
            fill_cbox()

    # def checker():
    #     # TODO FIX CHECKER
    #     def special_match(strg, search=re.compile(r'[^0-9.]').search):
    #         return not bool(search(strg))

    #     var = dlg.comboBoxTableSelect.currentText()
    #     try:
    #         if len(dlg.comboBoxSurface.currentText()) <1: 
    #             if var != 'Soil':
    #                 QMessageBox.warning(None, 'Surface Missing','Please select a surface')
    #                 return
    #         elif len(dlg.textEditDesc.value()) <1: 
    #             QMessageBox.warning(None, 'Description Missing','Please fill in the Description Box')
    #             return
    #         elif len(dlg.textEditOrig.value()) <1: 
    #             QMessageBox.warning(None, 'Origin Missing','Please fill in the Origin Box')
    #             return
    #         elif len(dlg.comboBoxRef.currentText()) <1:
    #             QMessageBox.warning(None, 'References Missing','Please select a references')
    #             return
    #     except:
    #         pass 
        
    #     table = db_dict[var]


    #     len_list = len(col_list)
    #     col_list =['General Type', 'Surface']

    #     for idx in range(len_list):
    #         # Left side
    #         Oc = eval('dlg.textBrowser_' + str(idx))
    #         oldField = Oc.toPlainText()
    #         vars()['dlg.textBrowser_' + str(idx)] = Oc
    #         # Right Side
    #         Nc = eval('dlg.textEdit_Edit_' + str(idx))

    #         if(len(Nc.value())) <1:
    #             # Something strange with OHM here!!!!!!!!!!!!!!!!!!!!!!!!!!
    #             QMessageBox.warning(None, oldField + ' Missing','Enter value for ' + oldField)
    #             break

    #         if Oc.toPlainText() != 'Season': # Add more to where this is fine!
    #             if  special_match(Nc.value()) == False:
    #                 QMessageBox.warning(None, oldField + ' Error','Invalid characters in ' + oldField + '\nOnly 0-9 and . are allowed')
    #                 break
    #         try:
    #             newField = float(Nc.value())
    #             # vars()['dlg.textEdit_Edit_' + str(idx)] = Nc
    #             # dict_reclass[oldField] =  [newField]
    #             # col_list.append(Oc.toPlainText())

    #             # dict_reclass['Ref'] = ref[ref['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
    #             # df_new_edit = pd.DataFrame(dict_reclass)
    #             # col_list.append('Ref')

    #             # row = len(table.index)
    #             # col = len(table[col_list].columns)

    #             try:
    #                 if var == 'Albedo':
    #                     if float(dlg.textEdit_Edit_0.value()) < 0 or float(dlg.textEdit_Edit_0.value()) > 1:
    #                         QMessageBox.warning(None, 'Albedo Min error','Alb_min must be between 0-1')
    #                         return
    #                     elif float(dlg.textEdit_Edit_1.value()) < 0 or float(dlg.textEdit_Edit_1.value()) > 1:
    #                         QMessageBox.warning(None, 'Albedo Max error','Alb_max must be between 0-1')
    #                         return
    #                     elif float(dlg.textEdit_Edit_0.value()) > float(dlg.textEdit_Edit_1.value()):
    #                         QMessageBox.warning(None, 'Value error', dlg.textBrowser_0.toPlainText() + ' must be smaller or equal to ' + dlg.textBrowser_1.toPlainText())
    #                         return

    #                 elif var == 'Leaf Area Index':

    #                     if float(dlg.textEdit_Edit_1.value()) < 0 or float(dlg.textEdit_Edit_1.value()) > 1:
    #                         QMessageBox.warning(None, 'LAImin error','LAImin must be between 0-1')
    #                         return
    #                     elif float(dlg.textEdit_Edit_2.value()) < 0 or float(dlg.textEdit_Edit_2.value()) > 1:
    #                         QMessageBox.warning(None, 'LAImax error','LAImax must be between 0-1')
    #                         return
    #                     elif float(dlg.textEdit_Edit_1.value()) > float(dlg.textEdit_Edit_2.value()):
    #                         QMessageBox.warning(None, 'Value error', dlg.textBrowser_1.toPlainText() + ' must be smaller or equal to ' + dlg.textBrowser_2.toPlainText())
    #                         return
    #                     elif int(dlg.textEdit_Edit_0.value()) > 1:
    #                         QMessageBox.warning(None, 'LAI Equation error','LAIeq choices are 0 or 1')
    #                         return

    #                 elif var == 'Porosity':
    #                     if float(dlg.textEdit_Edit_0.value()) > float(dlg.textEdit_Edit_1.value()):
    #                         QMessageBox.warning(None, 'Value error', dlg.textBrowser_0.toPlainText() + ' must be smaller or equal to ' + dlg.textBrowser_1.toPlainText())
    #                         return

    #                 elif var == 'Emissivity':
    #                     if float(dlg.textEdit_Edit_0.value()) < 0 or float(dlg.textEdit_Edit_0.value()) > 1:
    #                         QMessageBox.warning(None, 'Emissivity error','Emissivity must be between 0-1')
    #                         return
    #                 elif var == 'Conductance':
    #                     if float(dlg.textEdit_Edit_11.value()) <1 or float(dlg.textEdit_Edit_11.value()) >2:
    #                         QMessageBox.warning(None, 'gsModel error','gsModel Choices are 1 & 2')
    #                         return

    #                 for i in range(row):
    #                     checker = 0
    #                     for j in range(col):
    #                         if table[col_list].iloc[i].tolist()[j] == df_new_edit.iloc[0].tolist()[j]:
    #                             checker = checker+1
    #                     if checker == col:
    #                         QMessageBox.information(None, 'Information',
    #                             'Another entry in the database with same Values and Referece is found in the Database' +
    #                             '\n\n[ ' +  str(table.loc[table.index[i], 'Description']) + ', ' + str(table.loc[table.index[i], 'Origin']) + 
    #                             ', ' + str(table.loc[table.index[i], 'References'] + ' ]' +
    #                             '\n\nYou are able to add the entry if you think this is different from what already exist in the database!'))
                
    #             except:
    #                 pass
    #         except:
    #             pass

    dlg.comboBoxTableSelect.currentIndexChanged.connect(table_changed) 
    dlg.pushButtonGen.clicked.connect(add_table)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
