import pandas as pd
from .database_functions import save_to_db, create_code
from qgis.PyQt.QtWidgets import QMessageBox



#################################################################################################
#                                                                                               #
#                                  Reference manager                                            #
#                                                                                               #
#################################################################################################
def setup_ref_manager(self, dlg, db_dict, db_path):

    def fill_cboxes():
        dlg.comboBoxRef.clear()
        dlg.textEditYear.clear()
        dlg.textEditTitle.clear(),
        dlg.textEditJournal.clear(),
        dlg.textEditDOI.clear()
        for i in range(0,16):
            first_name = eval('dlg.textEditFN_' + str(i))
            last_name = eval('dlg.textEditLN0_' + str(i))   
            first_name.clear()
            last_name.clear()
            
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)

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

    def check_reference():

        dlg.pushButtonAddRef.setEnabled(True)
        author_list = []
        for i in range(0,16):
            first_name = eval('dlg.textEditFN_' + str(i))
            last_name = eval('dlg.textEditLN0_' + str(i))   
            name = first_name.value() + ', ' + last_name.value() + ';' 
            if len(first_name.value()) > 0 and len(last_name.value()) > 0: 
                author_list.append(name)

        # ref_dict = {
        #     'Author' : (' '.join(author_list)),
        #     'Publication Year' : dlg.textEditYear.value(),
        #     'Title' : dlg.textEditTitle.value(),
        #     'Journal' : dlg.textEditJournal.value(),
        #     'DOI' : dlg.textEditDOI.value()
        # }

        # QMessageBox.information(None, 'Sucessful','Your reference is compatible. \n Press Add Refernce to add to your Local Database')

    # def add_reference():
    #     Type, veg, nonveg, water, ref, alb, em, OHM, LAI, st, cnd, LGP, dr, VG, ANOHM, BIOCO2, MVCND, por, reg, snow, AnEm, prof, ws, soil, ESTM, irr , country= self.read_db()
    #     author_list = []
    #     for i in range(0,16):
    #         first_name = eval('dlg.textEditFN_' + str(i))
    #         last_name = eval('dlg.textEditLN0_' + str(i))   
    #         name = first_name.value() + ', ' + last_name.value() + ';' 
    #         if len(first_name.value()) > 0 and len(last_name.value()) > 0: 
    #             author_list.append(name)

    #     ref_dict = {
    #         'ID' : 'Ref' + str(int(round(time.time()))),
    #         'Author' : (' '.join(author_list)),
    #         'Publication Year' : dlg.textEditYear.value(),
    #         'Title' : dlg.textEditTitle.value(),
    #         'Journal' : dlg.textEditJournal.value(),
    #         'DOI' : dlg.textEditDOI.value()
    #     }

    #     new_edit_ref = pd.DataFrame(ref_dict, index=[0]).set_index('ID')
    #     ref = ref.append(new_edit_ref)
    #     self.write_to_db(Type, veg, nonveg, water, ref, alb, em, OHM, LAI, st, cnd, LGP, dr, VG, ANOHM, BIOCO2, MVCND, por, reg, snow, AnEm, prof, ws, soil, ESTM, irr)
    #     self.setup_tabs()
    #     self.dlg.tabWidget.setCurrentIndex(10)
    #     QMessageBox.information(None, 'Sucessful','Reference Added to Local database')


    def add_ref():

        author_list = []
        for i in range(0,16):
            first_name = eval('dlg.textEditFN_' + str(i))
            last_name = eval('dlg.textEditLN0_' + str(i))   
            name = first_name.value() + ', ' + last_name.value() + ';' 
            if len(first_name.value()) > 0 and len(last_name.value()) > 0: 
                author_list.append(name)

        ref_dict = {
            'ID' : create_code('Reference'),
            'Author' : (' '.join(author_list)),
            'Publication Year' : dlg.textEditYear.value(),
            'Title' : dlg.textEditTitle.value(),
            'Journal' : dlg.textEditJournal.value(),
            'DOI' : dlg.textEditDOI.value()
        }

        new_edit = pd.DataFrame([ref_dict]).set_index('ID')
        db_dict['References'] = pd.concat([db_dict['References'], new_edit])
        save_to_db(db_path, db_dict)

        QMessageBox.information(None, 'Succesful', 'New edit added to your local database')
        fill_cboxes()

    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 9:
            fill_cboxes()

    # dlg.pushButtonCheck.clicked.connect(check_reference)
    dlg.pushButtonAddRef.clicked.connect(add_ref)            
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
