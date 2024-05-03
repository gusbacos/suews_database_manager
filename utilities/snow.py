import pandas as pd
from .database_functions import save_to_db, create_code
from qgis.PyQt.QtWidgets import QMessageBox

#################################################################################################
#                                                                                               #
#                                  Snow Creator                                                 #
#                                                                                               #
#################################################################################################
def setup_snow_creator(self, dlg, db_dict, db_path ):
    dlg.comboBoxBase.addItems(db_dict['Snow']['descOrigin'].tolist())
    dlg.comboBoxBase.setCurrentIndex(-1)

    cbox_dict = {
        'Alb' : alb[alb['General Type'] == 'Snow'],
        'Em' : em[em['General Type'] == 'Snow'],
        'OHMCode_WinterWet' : OHM[OHM['General Type'] == 'Snow'],
        'OHMCode_WinterDry' : OHM[OHM['General Type'] == 'Snow'],
        'OHMCode_SummerWet' : OHM[OHM['General Type'] == 'Snow'],
        'OHMCode_SummerDry' : OHM[OHM['General Type'] == 'Snow'],
        'ESTM' : ESTM[ESTM['General Type'] == 'Snow'],
        'ANOHM' : ANOHM[ANOHM['General Type'] == 'Snow']
        }

    for i in range(0, 8): 
        Tb = eval('dlg.textBrowserCb_' + str(i))
        Cb = eval('dlg.comboBox_' + str(i))
        if len(Tb.toPlainText()) <1:
            break
        else:
            Cb.addItems((cbox_dict[Tb.toPlainText()])['descOrigin'].tolist())
            Cb.setCurrentIndex(-1)
    
    def base_snow_changed():

        base_snow = dlg.comboBoxBase.currentText()
        snow_sel = snow[snow['descOrigin'] == base_snow]

        snow_sel_dict = snow_sel.squeeze().to_dict()
        
        for i in range(0,11):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.LineEdit_' + str(i))
            Le.clear()
            Le.setText(str(snow_sel_dict[Tb.toPlainText()]))
        
        for i in range(0,8):
            Cb = eval('dlg.comboBox_' + str(i))
            CbT = eval('dlg.textBrowserCb_' + str(i))
            cbox_list = cbox_dict[CbT.toPlainText()].index.tolist()
            list_indexcer = snow_sel_dict[CbT.toPlainText()]
            Cb.setCurrentIndex(cbox_list.index(list_indexcer))

    def add_snow():
        Type, veg, nonveg, water, ref, alb, em, OHM, LAI, st, cnd, LGP, dr, VG, ANOHM, BIOCO2, MVCND, por, reg, snow, AnEm, prof, ws, soil, ESTM, irr , country= self.read_db()
        dict_reclass = {
            'ID' : create_code('Snow'),
            'Description' : dlg.textEditDesc.value(),
            'Origin' : dlg.textEditOrig.value()
        }
        
        for i in range(0, 8): 
            Tb = eval('dlg.textBrowserCb_' + str(i))
            Cb = eval('dlg.comboBox_' + str(i))
            col = Tb.toPlainText()
            val = Cb.currentText()
            table = cbox_dict[col]
            fill = table[table['descOrigin'] == val].index.item()   
            dict_reclass[col] = [fill]

        for i in range(0, 11): 
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.LineEdit_' + str(i))
            dict_reclass[Tb.toPlainText()] = [Le.text()]

        df_new_edit = pd.DataFrame(dict_reclass).set_index('ID')
        snow = snow.append(df_new_edit)
        self.write_to_db(Type, veg, nonveg, water, ref, alb, em, OHM, LAI, st, cnd, LGP, dr, VG, ANOHM, BIOCO2, MVCND, por, reg, snow, AnEm, prof, ws, soil, ESTM, irr)
        self.setup_tabs()
        self.dlg.tabWidget.setCurrentIndex(7)
        QMessageBox.information(None, 'Succesful', 'Snow Entry added to your local database')

    dlg.comboBoxBase.currentIndexChanged.connect(base_snow_changed)
    dlg.pushButtonGen.clicked.connect(add_snow) 