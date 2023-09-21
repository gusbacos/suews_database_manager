import pandas as pd
from .database_functions import save_to_db, create_code


#################################################################################################
#                                                                                               #
#                                  Antrhopogenic Emission Manager                               #
#                                                                                               #
#################################################################################################

def setup_anthropogenic_emission_manager(self, dlg, db_dict, db_path):
    dlg.comboBoxBaseAnEm.addItems(db_dict['AnthropogenicEmission']['descOrigin'].tolist())
    dlg.comboBoxBaseAnEm.setCurrentIndex(-1)
    dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
    dlg.comboBoxRef.setCurrentIndex(-1)
    # for i in range(0,8):
    #     Cb = eval('dlg.comboBoxAnEm_' + str(i))
    #     Cb.clear()
    #     # Cb.addItems((prof['descOrigin'][prof['Profile Type'] == 'Anthropogenic heat flux']).tolist())
    #     Cb.setCurrentIndex(-1)

    def base_AnEm_changed():

        base_irr = dlg.comboBoxBaseAnEm.currentText()
        AnEm_sel = db_dict['AnthropogenicEmission'][db_dict['AnthropogenicEmission']['descOrigin'] == base_irr]

        AnEm_sel_dict = AnEm_sel.squeeze().to_dict()
        # prof_sel = (prof[prof['Profile Type'] == 'Anthropogenic heat flux']).index.tolist()
        
        for i in range(1,31):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.lineEdit_' + str(i))
            Le.clear()
            Le.setText(str(AnEm_sel_dict[Tb.toPlainText()]))
        
        # for i in range(0,8):
        #     Cb = eval('dlg.comboBoxAnEm_' + str(i))
        #     CbT = eval('dlg.textBrowserCb_' + str(i))
        #     prof_id = AnEm_sel_dict[CbT.toPlainText()]
        #     # Cb.setCurrentIndex(prof_sel.index(prof_id))
    
    def ref_changed():
        dlg.textBrowserRef.clear()

        try:
            ID = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item()
            dlg.textBrowserRef.setText(
                '<b>Author: ' +'</b>' + str(ref.loc[ID, 'Author']) + '<br><br><b>' +
                'Year: ' + '</b> '+ str(ref.loc[ID, 'Publication Year']) + '<br><br><b>' +
                'Title: ' + '</b> ' +  str(ref.loc[ID, 'Title']) + '<br><br><b>' +
                'Journal: ' + '</b>' + str(ref.loc[ID, 'Journal']) + '<br><br><b>'
            )
        except:
            pass

    def add_AnEm():
        Type, veg, nonveg, water, ref, alb, em, OHM, LAI, st, cnd, LGP, dr, VG, ANOHM, BIOCO2, MVCND, por, reg, snow, AnEm, prof, ws, soil, ESTM, irr, country = self.read_db()
        profIndex = prof.copy()
        profIndex['descOrigin'] = profIndex['Profile Type'] + ', ' + profIndex['Description'] + ', ' +  profIndex['Origin']
        prof_sel = (profIndex[profIndex['Profile Type'] == 'Anthropogenic heat flux'])

        dict_reclass = {
            'ID' : ('Prof' + str(int(round(time.time())))),
            'Description' : dlg.textEditDesc.value(),
            'Origin' : dlg.textEditOrig.value(),
        }
        for i in range(0,30):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.AnEmLineEdit_' + str(i))
            col = Tb.toPlainText()
            val = Le.text()
            dict_reclass[col] = val
        
        for i in range(0,8):
            Cb = eval('dlg.comboBoxAnEm_' + str(i))
            CbT = eval('dlg.textBrowserCb_' + str(i))
            col = CbT.toPlainText()
            val = prof_sel[prof_sel['descOrigin'] == Cb.currentText()].index.item()
            dict_reclass[col] = val

        df_new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        AnEm = AnEm.append(df_new_edit)

    dlg.pushButtonGen.clicked.connect(add_AnEm)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed)
    dlg.comboBoxBaseAnEm.currentIndexChanged.connect(base_AnEm_changed)

