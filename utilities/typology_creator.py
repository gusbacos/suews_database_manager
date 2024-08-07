from qgis.PyQt.QtWidgets import QMessageBox
import pandas as pd
from .database_functions import create_code, save_to_db, surf_df_dict


#################################################################################################
#                                                                                               #
#                                  Land Cover                                                   #
#                                                                                               #
#################################################################################################

def setup_typology_creator(self, dlg, db_dict, db_path):
    
    dlg.comboBoxSurface.setCurrentIndex(-1)
    dlg.comboBoxProfileType.setCurrentIndex(-1)
    dlg.comboBoxBase.setCurrentIndex(-1)

    def changed_surface():

        # try:
        # # Clear and enable ComboBox
        dlg.comboBoxBase.clear()
        dlg.comboBoxBase.setEnabled(True)

        for i in range(0,20): 
            Oc = eval('dlg.textBrowser_' + str(i))
            Oc.clear()
            Oc.setDisabled(True)
            Nc = eval('dlg.comboBox_' + str(i))
            Nc.clear()
            Nc.setDisabled(True)         

        # Read what surface user has chosen
        surface = dlg.comboBoxSurface.currentText()

        # Select correct tab fom DB (Veg, NonVeg or Water)
        if surface == 'Buildings':
            dlg.textBrowserProfileType.setEnabled(True)
            dlg.comboBoxProfileType.setEnabled(True)
            dlg.comboBoxProfileType.setCurrentIndex(0)

        else: 
            dlg.textBrowserProfileType.setDisabled(True)
            dlg.comboBoxProfileType.setCurrentIndex(-1)
            dlg.comboBoxProfileType.setDisabled(True)

        table = db_dict[surf_df_dict[surface]]

        dlg.comboBoxBase.addItems(table['descOrigin'][table['Surface'] == surface])
        dlg.comboBoxBase.setCurrentIndex(0) # -1 before

        col_list = list(table)
        remove_cols = ['ID', 'Surface', 'Period', 'Origin', 'Description', 'Ref', 'typeOrigin', 'descOrigin', 'Color']

        if surface != 'Deciduous Tree':
            remove_cols.append('Porosity') # Exception for just Deciduous tree in Veg

        if surface != 'Water': # Exception for just Water
            remove_cols.append('Water State')

        if surface != 'Buildings':
            remove_cols.append('Spartacus Surface')
            remove_cols.append('ESTM')          

        for col in remove_cols:
            try:
                col_list.remove(col)
            except:
                pass
        
        for i in range(len(col_list)-1): 
            Oc = eval('dlg.textBrowser_' + str(i))
            Oc.clear()
            Oc.setEnabled(True)
            Nc = eval('dlg.comboBox_' + str(i))
            Nc.clear()
            Nc.setEnabled(True)

            table_name_str = col_list[i]

        #     # Fill in name of table
            Oc.setText(table_name_str)


            if table_name_str == 'Spartacus Surface':
                table_sel = db_dict[table_name_str]     
                table_surf = table_sel.drop(columns =['descOrigin'])
                table_sel = table_sel.reset_index().drop(columns = ['ID'])

            else:
                
                if table_name_str.startswith('OHM'):
                    table = table_name_str = 'OHM'

                table = db_dict[table_name_str]
                table_surf = table[table['Surface'] == surface]

                table_sel = table_surf.drop(columns =['Surface']).reset_index()
                if table_name_str.startswith('OHM'):
                    if surface == 'Grass' or surface == 'Evergreen Tree' or surface == 'Deciduous Tree':
                        table_surf2 = table[table['Surface'] == 'All vegetation']
                        table_surf = pd.concat([table_surf, table_surf2])
                    if surface == 'Buildings' or surface == 'Paved' or surface == 'Bare Soil':
                        table_surf2 = table[table['Surface'] == 'All Nonveg']
                        table_surf = pd.concat([table_surf, table_surf2])
                        # a = 7/0
                try :
                    table_surf.drop(columns =['descOrigin'])
                except:
                    pass

                table_sel = table_sel.drop(columns = ['ID'])

            Nc_fill_list = []
            idx = 0
            for desc, orig, idx in zip(table_surf['Description'].tolist() ,table_surf['Origin'].tolist(), list(range(len(table_surf['Origin'].tolist())))):
                Nc_fill_list.append((str(idx) + ': ' + str(desc) + ', ' + str(orig)))
            
            Nc.addItems(Nc_fill_list)
        # except:
        #     pass
        #     print('ops')
    
    def base_typology_changed():

        if dlg.comboBoxBase.currentIndex() != -1: # only do below if a base typology is selected

            surface = dlg.comboBoxSurface.currentText()
            base_typology = dlg.comboBoxBase.currentText()

            surface_table = db_dict[surf_df_dict[surface]]
            surface_sel = surface_table[surface_table['Surface'] == surface]
            surf_row = surface_sel[surface_sel['descOrigin'] == base_typology]    
            surf_row_dict = surf_row.squeeze().to_dict()

            dlg.textEditDesc.setText(surf_row['Description'].item())
            dlg.textEditOrig.setText(surf_row['Origin'].item())

            for i in range(0,21):
                Cb = eval('dlg.comboBox_' + str(i))
                Tb = eval('dlg.textBrowser_' + str(i))

                if len(Tb.toPlainText()) <1:
                    break
                else: 

                    cbox_table_indexer = Tb.toPlainText()
                    surf_row_id = surf_row_dict[cbox_table_indexer]
                    
                    if cbox_table_indexer.startswith('OHM'):
                        cbox_table = db_dict['OHM']
                    else:      
                        cbox_table = db_dict[cbox_table_indexer]

                    if cbox_table_indexer == 'Spartacus Surface':
                            cbox_index = (cbox_table['descOrigin'].tolist()).index(cbox_table.loc[surf_row_id, 'descOrigin'])
                    else:
                        cbox_index = (cbox_table['descOrigin'][cbox_table['Surface'] == surface].tolist()).index(cbox_table.loc[surf_row_id, 'descOrigin'])
                    Cb.setCurrentIndex(cbox_index)

    def print_table(idx):

        surface = dlg.comboBoxSurface.currentText()
        try:
            Tb_name = eval('dlg.textBrowser_' + str(idx))
            table_var = Tb_name.toPlainText()

            if table_var.startswith('OHM'):
                table = db_dict['OHM']
            else:
                table = db_dict[table_var]

            dlg.textBrowserTableLable.setText(table_var)

            if table_var == 'Spartacus Surface':
                
                Tb = eval('dlg.textBrowserEl')
                Tb.clear()
                ref_show = db_dict['References']['authorYear'].to_dict()
                table['Reference'] = '' 
                try:
                    for i in range(len(table)):
                        table['Reference'].iloc[i] = ref_show[table['Ref'].iloc[i]] 
                except:
                    pass 
                Tb.setText(str(table.drop(columns = ['ID', 'Ref']).to_html(index=True)))
                Tb.setLineWrapMode(0)
                
            else:
                
                table_surf = table[table['Surface'] == surface]

                # table_sel = table_surf.drop(columns =['Surface']).reset_index()
                if table_var.startswith('OHM'):
                    if surface == 'Grass' or surface == 'Evergreen Tree' or surface == 'Deciduous Tree':
                        table_surf2 = table[table['Surface'] == 'All vegetation']
                        table_surf = pd.concat([table_surf, table_surf2])
                    if surface == 'Buildings' or surface == 'Paved' or surface == 'Bare Soil':
                        table_surf2 = table[table['Surface'] == 'All Nonveg']
                        table_surf = pd.concat([table_surf, table_surf2])

                try:
                    # table = table[table['Surface'] == surface].drop(columns = ['General Type', 'Surface', 'descOrigin']).reset_index()
                    table = table_surf.drop(columns = ['General Type', 'Surface', 'descOrigin']).reset_index()
                except:
                    # table = table[table['Surface'] == surface].drop(columns = ['General Type', 'Surface']).reset_index()
                    table = table_surf.drop(columns = ['General Type', 'Surface']).reset_index()
                Tb = eval('dlg.textBrowserEl')
                Tb.clear()
                ref_show = db_dict['References']['authorYear'].to_dict()
                table['Reference'] = '' 
                try:
                    for i in range(len(table)):
                        table['Reference'].iloc[i] = ref_show[table['Ref'].iloc[i]] 
                except:
                    pass 
                Tb.setText(str(table.drop(columns = ['ID', 'Ref']).to_html(index=True)))
                Tb.setLineWrapMode(0)
        except:
            pass

    def check_typology(): # Add more checkers
        if len(dlg.comboBoxSurface.currentText()) <1: 
            QMessageBox.warning(None, 'Surface Missing','Please select a surface')
            pass
        elif len(dlg.textEditDesc.text()) <1: 
            QMessageBox.warning(None, 'Description Missing','Please fill in the Description Box')
            pass
        elif len(dlg.textEditOrig.text()) <1: 
            QMessageBox.warning(None, 'Origin Missing','Please fill in the Origin Box')
            pass
        else:
            generate_typology()
        
        
    def generate_typology():

        # Nonveg or veg or water?
        surface = dlg.comboBoxSurface.currentText()

        table = db_dict[surf_df_dict[surface]]
        col_list = list(table)
        remove_cols = ['ID', 'Description', 'Surface', 'Period', 'Origin', 'Type', 'descOrigin']
        
        if surface != 'Water':
            remove_cols.append('Water State')
        if surface == 'Grass' or surface == 'Evergreen Tree':
            remove_cols.append('Porosity')
        for col in remove_cols:
            try:
                col_list.remove(col)
            except:
                pass

        dict_reclass = {
            'ID' : create_code(surf_df_dict[surface]),
            'Surface' : surface,
            'Origin' : str(dlg.textEditOrig.value()),
            'Description' : str(dlg.textEditDesc.value()),
        }
        for i in range(0,21):
            Nc = eval('dlg.comboBox_' + str(i))
            Oc = eval('dlg.textBrowser_' + str(i))
            
            if len(Oc.toPlainText()) <1:
                break
            else:
                oldField = Oc.toPlainText()
                sel_att = Nc.currentText()

                if oldField.startswith('OHM'):  
                    table = db_dict['OHM']
                else:               
                    table = db_dict[oldField]
                sel_att = sel_att.split(': ')[1] # Remove number added for interpretation in GUI

                newField = table.loc[table['descOrigin'] == sel_att].index.item()
                dict_reclass[oldField] = newField
                table.drop(columns = 'descOrigin')
            
        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')

        # Add new line to correct tab veg, nonveg or water
        if surface == 'Paved': 
            new_edit['Water State'] = 424
        elif surface == 'Buildings':
            new_edit['Period'] = dlg.comboBoxProfileType.currentText()
            new_edit['Water State'] = 424
        elif surface == 'Bare Soil':
            new_edit['Water State'] = 425
        elif surface == 'Grass':
            new_edit['Water State'] = 428
            new_edit['Porosity'] = 3411
        elif surface == 'Deciduous Tree':
            new_edit['Water State'] = 427
        elif surface == 'Evergreen Tree':
            new_edit['Water State'] = 426
            new_edit['Porosity'] = 3410
        
        db_dict[surf_df_dict[surface]] = pd.concat([db_dict[surf_df_dict[surface]], new_edit])
    
        save_to_db(db_path, db_dict)
        dlg.comboBoxSurface.setCurrentIndex(-1)
        dlg.comboBoxProfileType.setCurrentIndex(-1)
        dlg.comboBoxBase.setCurrentIndex(-1)
        dlg.textEditDesc.clear()
        dlg.textEditOrig.clear()
        
        QMessageBox.information(None, 'Sucessful','Typology entry added to local database')

        # self.dlg.tabWidget.setCurrentIndex(2)

    dlg.pushButtonGen.clicked.connect(check_typology)
    dlg.comboBoxBase.currentIndexChanged.connect(base_typology_changed)
    dlg.comboBoxSurface.currentIndexChanged.connect(changed_surface)

    dlg.comboBox_1.highlighted.connect(lambda: print_table(1))
    dlg.comboBox_2.highlighted.connect(lambda: print_table(2))
    dlg.comboBox_3.highlighted.connect(lambda: print_table(3))
    dlg.comboBox_4.highlighted.connect(lambda: print_table(4))
    dlg.comboBox_5.highlighted.connect(lambda: print_table(5))
    dlg.comboBox_6.highlighted.connect(lambda: print_table(6))
    dlg.comboBox_7.highlighted.connect(lambda: print_table(7))
    dlg.comboBox_8.highlighted.connect(lambda: print_table(8))
    dlg.comboBox_9.highlighted.connect(lambda: print_table(9))
    dlg.comboBox_10.highlighted.connect(lambda: print_table(10))
    dlg.comboBox_11.highlighted.connect(lambda: print_table(11))
    dlg.comboBox_12.highlighted.connect(lambda: print_table(12))
    dlg.comboBox_13.highlighted.connect(lambda: print_table(13))
    dlg.comboBox_14.highlighted.connect(lambda: print_table(14))
    dlg.comboBox_15.highlighted.connect(lambda: print_table(15))
    dlg.comboBox_16.highlighted.connect(lambda: print_table(16))
    dlg.comboBox_17.highlighted.connect(lambda: print_table(17))
    dlg.comboBox_18.highlighted.connect(lambda: print_table(18))
    dlg.comboBox_19.highlighted.connect(lambda: print_table(19))
    dlg.comboBox_20.highlighted.connect(lambda: print_table(20))
    dlg.comboBox_0.highlighted.connect(lambda: print_table(0))